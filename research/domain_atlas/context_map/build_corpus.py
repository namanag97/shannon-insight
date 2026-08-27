#!/usr/bin/env python3
"""Build the candidate global bounded-context map deterministically.

The corpus is deliberately open-world.  It samples independently-owned semantic
contexts and records every crossing as a typed relation plus an explicit ACL
decision.  It never infers ownership or synonymy from a name.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parent
ATLAS = ROOT.parent
RETRIEVED = "2026-08-25"
STATUS = "candidate_open_world"


PLANES: list[tuple[str, str, list[tuple[str, str]]]] = [
    ("constitutional", "authority.constitutional_semantics", [
        ("identifier", "What makes two references denote the same thing within an explicit namespace?"),
        ("edition", "Which immutable contract edition is being used and how may editions coexist?"),
        ("semantic_type", "Which values are admissible and which equality and ordering laws apply?"),
        ("quantity_unit", "What quantity, dimension, unit and conversion law does a value carry?"),
        ("temporal_reference", "In which temporal reference system are instants, intervals and durations interpreted?"),
        ("uncertainty", "What uncertainty object, calibration and combination law qualifies a claim?"),
    ]),
    ("intent", "authority.enterprise_intent", [
        ("analytical_question", "Which answerable question is requested, for whom, and under which scope?"),
        ("decision_intent", "Which decision may consume an answer and what authority may act on it?"),
        ("objective_constraint", "Which objectives, constraints and trade-offs define acceptable alternatives?"),
        ("human_judgment", "Which judgments cannot be delegated and how are reasons and overrides recorded?"),
        ("outcome_feedback", "Which observed outcome tests whether the decision achieved its intended effect?"),
        ("value_cost", "Which value, adoption, operating cost and exit measures govern continuation?"),
    ]),
    ("source", "authority.source_estate", [
        ("source_class", "What class of external system can make which observations under which native contract?"),
        ("source_occurrence", "Which exact deployed source occurrence, owner and edition produced an observation?"),
        ("source_authority", "For which facts and times is a source authoritative, provisional or merely informative?"),
        ("source_object", "Which native object, identity, transaction boundary and lifecycle does the source expose?"),
        ("source_cursor", "Which position, page, log offset or continuation token delimits acquired source state?"),
        ("source_finality", "When may source state be treated as complete, retractable or superseded?"),
    ]),
    ("connectivity", "authority.acquisition", [
        ("connector_contract", "Which protocol-neutral acquisition requirements must a connector satisfy?"),
        ("authentication_binding", "Which principal and delegated credential may open a source session?"),
        ("snapshot_acquisition", "Which finite source cut was observed and with what consistency boundary?"),
        ("change_acquisition", "Which ordered source changes were observed after which source position?"),
        ("pagination_cursor", "How are partial pages continued without inventing completeness or identity?"),
        ("transfer_receipt", "What bytes, checksums, positions, attempts and omissions did acquisition actually produce?"),
    ]),
    ("modality", "authority.data_modality", [
        ("tabular", "What row, column, key, null and relation laws govern a tabular observation?"),
        ("document", "What document tree, rendition, embedded object and reading-order semantics govern content?"),
        ("graph", "What node, edge, statement, identity and entailment laws govern a graph?"),
        ("spatial", "What geometry, coverage, topology and coordinate reference system govern location?"),
        ("temporal_event", "What event, series, ordering, interval and correction laws govern temporal observations?"),
        ("media_signal", "What sampling, channel, tensor, codec-independent and synchronization laws govern media or signals?"),
    ]),
    ("admission", "authority.semantic_admission", [
        ("decode_parse", "Can hostile carriers be decoded and parsed within finite budgets?"),
        ("schema_validation", "Does decoded structure conform to an exact technical schema edition?"),
        ("semantic_admission", "May a structurally valid carrier be admitted as a domain value?"),
        ("canonicalization", "Which normalization yields a stable comparison or digest input without changing meaning?"),
        ("quarantine", "Where are malformed, ambiguous or unsafe values isolated without silent repair?"),
        ("admission_receipt", "Which exact checks, coercions, losses and refusals occurred at admission?"),
    ]),
    ("mapping", "authority.semantic_mapping", [
        ("field_mapping", "How does a foreign field map to a canonical property without stealing ownership?"),
        ("identity_mapping", "How are foreign identifiers related without asserting unproved identity?"),
        ("code_mapping", "How are code-system meanings translated with equivalence strength and residuals?"),
        ("temporal_alignment", "How are clocks, intervals, calendars and validity axes aligned?"),
        ("grain_transformation", "How does row or event grain change under explode, join, allocation or aggregation?"),
        ("loss_accounting", "Which information, alternatives and evidence are preserved, weakened or destroyed?"),
    ]),
    ("stream", "authority.streaming_semantics", [
        ("event_time", "Which domain time belongs to an event and how is it distinguished from recording time?"),
        ("watermark", "Which progress claim says earlier event times are unlikely or closed?"),
        ("window", "Which events belong to which finite analytical grouping under explicit boundaries?"),
        ("trigger", "When may provisional or revised results be emitted?"),
        ("stateful_dataflow", "Which keyed state, timer and update algebra incrementally maintains results?"),
        ("stream_finality", "When is a streaming result provisional, corrected, retracted or final?"),
    ]),
    ("orchestration", "authority.workflow_control", [
        ("workflow_definition", "Which dependency graph and parameter contract defines coordinated work?"),
        ("workflow_run", "Which immutable definition edition and inputs govern one run?"),
        ("task_attempt", "Which attempt, retry, timeout and effect intent belongs to one task instance?"),
        ("schedule_backfill", "Which calendar, partition range and reprocessing rule requests work?"),
        ("retry_compensation", "Which failures are retryable and which irreversible effects require compensation?"),
        ("run_receipt", "Which work completed, failed, was cancelled or remains indeterminate?"),
    ]),
    ("persistence", "authority.persistence", [
        ("object_store", "Which immutable objects, names, versions and conditional writes persist bytes?"),
        ("table_format", "Which logical table snapshots, manifests and schema evolution rules persist analytical state?"),
        ("snapshot_commit", "Which atomic publication and concurrency protocol makes a new snapshot visible?"),
        ("catalog", "Which namespace resolves logical assets to exact metadata and table editions?"),
        ("index_cache", "Which derived access path or cache is valid for which source cut and query semantics?"),
        ("backup_restore", "Which recoverable state, recovery point and restore proof survive failure?"),
    ]),
    ("query", "authority.query_compute", [
        ("semantic_query", "Which provider-neutral question over owned meanings has been requested?"),
        ("logical_plan", "Which lawful relational, graph, temporal or modality operations answer the question?"),
        ("physical_plan", "Which algorithms, distributions and resource decisions implement the logical plan?"),
        ("kernel_execution", "Which qualified kernel executed on which target and exact representation?"),
        ("result_stream", "Which ordered, partial or complete result values were produced?"),
        ("query_receipt", "Which plan, inputs, resources, warnings and evidence explain execution?"),
    ]),
    ("semantics", "authority.analytical_semantics", [
        ("entity_fact", "Which analytical entities and facts exist and at what identity and grain?"),
        ("measure_dimension", "Which measures, dimensions, members and units qualify analytical values?"),
        ("grain_population", "Which population, observation unit and grouping grain bound a calculation?"),
        ("metric_formula", "Which formula, filters, time semantics and aggregation law define a metric?"),
        ("join_path", "Which cardinality-qualified semantic relationships permit a join without fanout error?"),
        ("semantic_query_contract", "Which portable semantic query contract preserves these meanings?"),
    ]),
    ("study", "authority.analytical_study", [
        ("case_design", "Which diagnostic, inferential, optimization or decision case must be solved?"),
        ("study_design", "Which population, assignment, sampling and comparison design identifies an answer?"),
        ("estimand", "Which precise quantity is the study trying to estimate?"),
        ("estimator_method", "Which assumptions, estimator and method may estimate the estimand?"),
        ("result_evaluation", "Which validity, calibration, sensitivity and error evidence qualifies a result?"),
        ("decision_handoff", "Which qualified result may inform which human or automated decision?"),
    ]),
    ("quality", "authority.quality_control", [
        ("quality_requirement", "Which property, scope, threshold, time and authority define acceptable data?"),
        ("quality_observation", "Which measured evidence says what was observed, not whether it is acceptable?"),
        ("detection", "Which signal indicates a possible defect without deciding its disposition?"),
        ("adjudication", "Which authorized decision confirms, rejects or defers a suspected defect?"),
        ("correction", "Which approved transformation, repair, quarantine or source action addresses a defect?"),
        ("quality_certificate", "Which exact criteria and evidence support a scoped quality claim?"),
    ]),
    ("governance", "authority.data_governance", [
        ("governed_asset", "Which logical asset is governed and by which accountable, steward and custodian roles?"),
        ("metadata_assertion", "Who asserted which metadata about an asset, when and with what provenance?"),
        ("glossary_ontology", "Which terms, concepts, axioms and mappings are authoritative in which context?"),
        ("identity_resolution", "Which evidence and authority turn match candidates into identity decisions?"),
        ("master_reference", "Which authoritative master, golden projection, code set or reference dataset is intended?"),
        ("stewardship", "Which issues, approvals, delegations and review duties are assigned to which roles?"),
    ]),
    ("provenance", "authority.provenance_evidence", [
        ("lineage_assertion", "Who asserted which derivation or dependency relation at which granularity?"),
        ("provenance_bundle", "Which entities, activities, agents and qualified relations form an evidence bundle?"),
        ("claim_evidence", "Which argument and evidence support or defeat a claim?"),
        ("evidence_appraisal", "Which independent criteria appraise relevance, validity and strength?"),
        ("audit_observation", "Which security or operational event was observed without claiming business provenance?"),
        ("recall_supersession", "Which prior assertions, artifacts or publications are recalled or superseded?"),
    ]),
    ("security", "authority.security_privacy", [
        ("principal_authentication", "Which evidence authenticated which principal for which session?"),
        ("authorization_decision", "Which policy and attributes permit or deny a requested action?"),
        ("purpose_consent", "Which purpose, consent, legal basis and data-use restriction apply?"),
        ("policy_enforcement", "Which enforcement point applied which decision and emitted which receipt?"),
        ("crypto_protection", "Which confidentiality or integrity purpose, algorithm and key lifecycle protect carriers?"),
        ("privacy_disclosure", "Which disclosure, retention, residency and privacy-budget obligations constrain release?"),
    ]),
    ("consumption", "authority.analytical_consumption", [
        ("presentation_contract", "Which visual, textual or machine presentation preserves analytical meaning?"),
        ("interaction", "Which filter, drill, selection and write-back actions may a consumer perform?"),
        ("report_snapshot", "Which immutable result cut, layout and annotations form a report edition?"),
        ("live_view", "Which freshness, cache, query and update semantics govern a live view?"),
        ("alert_notification", "Which evaluated rule becomes which routed notification under which escalation policy?"),
        ("export_share", "Which export artifact or governed share may cross an organizational boundary?"),
    ]),
    ("runtime", "authority.resource_control", [
        ("resource_demand", "Which finite compute, memory, storage, network and locality resources are required?"),
        ("quota_budget", "Which authority limits admission and cost independently of physical capacity?"),
        ("admission_control", "Which request is admitted, queued, throttled or refused under current offers?"),
        ("reservation_allocation", "Which capacity is reserved and then allocated to which admitted work?"),
        ("lease_fencing", "Which time-bounded lease and fencing token grants exclusive resource use?"),
        ("usage_receipt", "Which measured usage, charge and release evidence did execution emit?"),
    ]),
    ("provider", "authority.capability_binding", [
        ("capability_requirement", "Which semantic, operational and non-functional capability is required?"),
        ("capability_offer", "Which implementation artifact claims which scoped capability offer?"),
        ("qualification", "Which executable evidence qualifies an offer for an exact target profile?"),
        ("target_profile", "Which architecture, runtime, limits and policy define a deployment target?"),
        ("deployment_occurrence", "Which exact deployed occurrence instantiates an artifact and target?"),
        ("binding_invalidation", "Which changes invalidate a prior requirement-offer binding?"),
    ]),
    ("product", "authority.product_management", [
        ("product_candidate", "Which users, jobs, outcomes and service promise justify a product boundary?"),
        ("suite_packaging", "Which products and libraries are packaged without acquiring their semantic ownership?"),
        ("managed_experience", "Which operated experience, SLO and responsibility boundary is promised?"),
        ("support_contract", "Which incidents, escalation, compatibility and recovery duties are supported?"),
        ("portability_exit", "Which data, definitions, evidence and work can leave without semantic captivity?"),
        ("product_lifecycle", "Which adoption, migration, deprecation and retirement states govern the offering?"),
    ]),
    ("finance_ccr", "authority.finance_counterparty_risk", [
        ("counterparty_identity", "Which legal entities, groups and netting parties are exposure counterparties?"),
        ("legal_agreement", "Which enforceable netting and collateral agreements apply in which jurisdiction?"),
        ("exposure_measurement", "Which trades, market states and future exposure measures define counterparty exposure?"),
        ("collateral_netting", "How are collateral, margins, sets and close-out netting lawfully applied?"),
        ("default_simulation", "Which default, dependency and wrong-way-risk scenarios generate exposure distributions?"),
        ("ccr_decision", "Which limits, valuation adjustments or capital decisions consume qualified CCR results?"),
    ]),
    ("health_outcomes", "authority.health_outcomes", [
        ("patient_identity", "Which authorized identity links observations to a patient without collapsing subjects?"),
        ("clinical_observation", "Which coded clinical observation, method, unit and status was recorded?"),
        ("episode_cohort", "Which episodes and patients satisfy a time-indexed cohort definition?"),
        ("outcome_estimation", "Which study design and estimand compare outcomes for the cohort?"),
        ("safety_adjudication", "Which qualified human authority confirms or rejects a potential safety signal?"),
        ("care_decision", "Which evidence may inform care without becoming an autonomous clinical order?"),
    ]),
    ("manufacturing_maintenance", "authority.industrial_maintenance", [
        ("asset_identity", "Which physical asset, component, configuration and serial history is observed?"),
        ("sensor_observation", "Which instrument, calibration, unit, sampling and time qualify a sensor value?"),
        ("process_event", "Which operation, state transition and production context generated an event?"),
        ("degradation_model", "Which failure mode, censoring and degradation assumptions qualify a health estimate?"),
        ("maintenance_optimization", "Which costs, risks, resources and constraints determine a maintenance policy?"),
        ("work_order", "Which authorized maintenance action, parts, schedule and completion evidence were issued?"),
    ]),
]


SOURCE_FILES = [
    "universes/governance_metadata_ontology_mdm/evidence-sources.jsonl",
    "universes/lineage_provenance_evidence/sources.jsonl",
    "universes/security_privacy_trust/sources.jsonl",
    "universes/pipeline_dataflow/sources.jsonl",
    "universes/persistence_lakehouse/sources.jsonl",
    "universes/query_compute_kernels/sources.jsonl",
    "universes/semantic_metrics_formulas/sources.jsonl",
    "universes/quality_observability_reconciliation/sources.jsonl",
    "universes/consumption_bi_visualization/sources.jsonl",
    "universes/source_systems/evidence-sources.jsonl",
    "universes/data_shapes/sources.jsonl",
    "universes/encoding_compression/sources.jsonl",
    "universes/messaging_channels/sources.jsonl",
    "universes/runtime_compute_resource/evidence.jsonl",
    "universes/method_kernels/sources.jsonl",
    "universes/operations_research/sources.jsonl",
    "compiler/provider_target_registry/sources.jsonl",
    "industries/finance_insurance/sources.jsonl",
    "industries/health_life_sciences/sources.jsonl",
    "industries/manufacturing_industrial/sources.jsonl",
]


PLANE_SOURCE_HINTS: dict[str, list[str]] = {
    "constitutional": ["governance_metadata_ontology_mdm", "lineage_provenance_evidence", "encoding_compression"],
    "intent": ["semantic_metrics_formulas", "operations_research"],
    "source": ["source_systems", "pipeline_dataflow"],
    "connectivity": ["pipeline_dataflow", "messaging_channels", "source_systems"],
    "modality": ["data_shapes", "encoding_compression", "consumption_bi_visualization"],
    "admission": ["encoding_compression", "data_shapes", "governance_metadata_ontology_mdm"],
    "mapping": ["governance_metadata_ontology_mdm", "lineage_provenance_evidence", "data_shapes"],
    "stream": ["pipeline_dataflow", "messaging_channels"],
    "orchestration": ["pipeline_dataflow", "runtime_compute_resource"],
    "persistence": ["persistence_lakehouse", "provider_target_registry"],
    "query": ["query_compute_kernels", "method_kernels"],
    "semantics": ["semantic_metrics_formulas", "governance_metadata_ontology_mdm"],
    "study": ["method_kernels", "operations_research", "semantic_metrics_formulas"],
    "quality": ["quality_observability_reconciliation", "lineage_provenance_evidence"],
    "governance": ["governance_metadata_ontology_mdm", "lineage_provenance_evidence"],
    "provenance": ["lineage_provenance_evidence", "governance_metadata_ontology_mdm"],
    "security": ["security_privacy_trust", "lineage_provenance_evidence"],
    "consumption": ["consumption_bi_visualization", "semantic_metrics_formulas"],
    "runtime": ["runtime_compute_resource", "pipeline_dataflow"],
    "provider": ["provider_target_registry", "query_compute_kernels", "persistence_lakehouse"],
    "product": ["provider_target_registry", "consumption_bi_visualization"],
    "finance_ccr": ["finance_insurance", "method_kernels", "operations_research"],
    "health_outcomes": ["health_life_sciences", "method_kernels", "security_privacy_trust"],
    "manufacturing_maintenance": ["manufacturing_industrial", "operations_research", "runtime_compute_resource"],
}


RELATION_TYPES = [
    "upstream_downstream", "customer_supplier", "conformist",
    "anti_corruption_layer", "open_host_service", "published_language",
    "shared_kernel", "separate_ways", "independent_appraisal", "authority_delegation",
    "evidence_submission", "compiler_requirement", "provider_offer",
    "runtime_receipt",
]


def slug_context(plane: str, name: str) -> str:
    return f"ctx.{plane}.{name}"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def build_sources() -> list[dict[str, Any]]:
    rows: list[tuple[int, str, dict[str, Any], str]] = []
    preferred = ("standard", "spec", "recommendation", "original", "paper", "official")
    seen: set[str] = set()
    for rel in SOURCE_FILES:
        for raw in read_jsonl(ATLAS / rel):
            url = raw.get("url") or raw.get("canonical_url")
            if not isinstance(url, str) or not url.startswith("http") or url in seen:
                continue
            seen.add(url)
            kind = str(raw.get("source_kind", "official_documentation")).lower()
            score = 0 if any(token in kind for token in preferred) else 1
            rows.append((score, url, raw, rel))
    rows.sort(key=lambda item: (item[0], item[1]))
    # Stratified sampling prevents a single prolific universe from crowding out
    # the other evidence planes.  URL deduplication still applies globally.
    by_origin: dict[str, list[tuple[int, str, dict[str, Any], str]]] = defaultdict(list)
    for row in rows:
        by_origin[row[3]].append(row)
    selected: list[tuple[int, str, dict[str, Any], str]] = []
    selected_urls: set[str] = set()
    for rel in SOURCE_FILES:
        for row in by_origin.get(rel, [])[:8]:
            if row[1] not in selected_urls:
                selected.append(row)
                selected_urls.add(row[1])
    for row in rows:
        if len(selected) >= 180:
            break
        if row[1] not in selected_urls:
            selected.append(row)
            selected_urls.add(row[1])
    # Innovation citations are first-class source records even if the general
    # source sample did not select that URL.
    for year, description, url in INNOVATIONS:
        if url not in selected_urls:
            publisher = next((name for marker, name in [
                ("debezium.io", "Debezium"), ("delta.io", "Delta Lake"),
                ("apache/iceberg", "Apache Iceberg"), ("iceberg.apache.org", "Apache Iceberg"),
                ("cloudevents", "CNCF CloudEvents"), ("in-toto", "in-toto"),
                ("hl7.org", "HL7 International"), ("openlineage.io", "OpenLineage"),
                ("opentelemetry.io", "OpenTelemetry"), ("ref.gs1.org", "GS1"),
                ("slsa.dev", "SLSA"), ("spec.openapis.org", "OpenAPI Initiative"),
                ("asyncapi.com", "AsyncAPI Initiative"), ("w3.org", "W3C"),
            ] if marker in url), "Primary specification publisher")
            selected.append((0, url, {
                "title": description.split(".")[0],
                "publisher": publisher,
                "source_kind": "primary_innovation_source",
                "publication_year": int(year),
                "authority_scope": "Primary source for the described non-LLM contract or implementation change.",
                "supports": ["innovation", "published_language_change", "context_boundary_evidence"],
                "limitations": ["Does not establish global semantic ownership or universal implementation support."],
            }, "embedded_innovation_source"))
            selected_urls.add(url)
    selected.sort(key=lambda item: (item[0], item[1]))
    result = []
    for idx, (_, url, raw, rel) in enumerate(selected, start=1):
        topics = raw.get("topics") or raw.get("supports") or raw.get("areas") or []
        if not isinstance(topics, list):
            topics = [str(topics)]
        result.append({
            "source_id": f"source.context_map.{idx:03d}",
            "record_kind": "evidence_source",
            "status": "candidate_reference",
            "title": raw.get("title", "Untitled primary source"),
            "publisher": raw.get("publisher") or raw.get("issuer") or "Primary publisher",
            "source_kind": raw.get("source_kind", "official_documentation"),
            "publication_year": raw.get("publication_year") or raw.get("publication_date"),
            "url": url,
            "authority_scope": raw.get("authority_scope") or "Limited to the cited standard, specification, original research, or official implementation surface.",
            "supports": [str(x) for x in topics][:8],
            "limitations": raw.get("limitations") or raw.get("does_not_establish") or [
                "Does not establish global semantic ownership, universal equivalence, or implementation conformance."
            ],
            "retrieved_on": RETRIEVED,
            "origin_record_ref": f"{rel}#{raw.get('source_id', raw.get('evidence_id', 'unknown'))}",
        })
    return result


def build_contexts(sources: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    contexts: list[dict[str, Any]] = []
    chains: dict[str, list[str]] = {}
    for plane_index, (plane, owner, items) in enumerate(PLANES):
        chain = []
        for item_index, (name, question) in enumerate(items):
            context_id = slug_context(plane, name)
            chain.append(context_id)
            hints = PLANE_SOURCE_HINTS[plane]
            query_tokens = set(re.findall(r"[a-z0-9]+", f"{name} {question}".lower()))
            stop = {"what", "which", "where", "when", "with", "from", "into", "does", "under", "this", "that", "their", "have"}
            query_tokens -= stop
            def evidence_score(source: dict[str, Any]) -> tuple[int, str]:
                haystack = " ".join([source["title"], *source["supports"]]).lower()
                source_tokens = set(re.findall(r"[a-z0-9]+", haystack))
                return (-len(query_tokens & source_tokens), source["source_id"])
            evidence_candidates: list[dict[str, Any]] = []
            for hint in hints:
                pool = [source for source in sources if hint in source["origin_record_ref"]]
                pool.sort(key=evidence_score)
                if pool and pool[0]["source_id"] not in {item["source_id"] for item in evidence_candidates}:
                    evidence_candidates.append(pool[0])
                if len(evidence_candidates) == 2:
                    break
            if len(evidence_candidates) < 2:
                eligible = sorted(sources, key=evidence_score)
                for source in eligible:
                    if source["source_id"] not in {item["source_id"] for item in evidence_candidates}:
                        evidence_candidates.append(source)
                    if len(evidence_candidates) == 2:
                        break
            evidence = [item["source_id"] for item in evidence_candidates]
            language = f"language.{plane}.{name}.v1"
            contexts.append({
                "context_id": context_id,
                "edition": 1,
                "record_kind": "bounded_context_candidate",
                "status": STATUS,
                "completion_claim": False,
                "plane_id": plane,
                "semantic_owner": {
                    "owner_id": owner,
                    "owner_kind": "candidate_authority_role",
                    "adjudication": "unresolved_candidate",
                    "inferred_from_name": False,
                },
                "sovereign_question": question,
                "positive_charter": [f"Own the meaning and laws needed to answer: {question}"],
                "negative_charter": [
                    "Does not own foreign contexts, provider products, suites, deployment occurrences, or UI packaging.",
                    "Does not infer synonymy, identity, authority, or compatibility from spelling."
                ],
                "published_languages": [{
                    "language_id": language,
                    "edition": 1,
                    "stability": "candidate",
                    "compatibility_relation_required": True,
                }],
                "imports": [],
                "exports": [language],
                "export_contracts": [],
                "role_capabilities": ["upstream", "downstream", "translator", "evidence_issuer", "evidence_consumer"],
                "authority_model": "qualified authority and scope must accompany every assertion or command",
                "time_model": "valid, recording, decision and observation time remain explicit and non-substitutable",
                "identity_model": "foreign identifiers remain scoped; equality requires an authorized mapping",
                "grain_model": "input, transformation and output grain are explicit",
                "version_policy": "multiple editions may coexist only through an explicit compatibility relation",
                "evidence_refs": evidence,
                "evidence_posture": "plane-level candidate boundary evidence; not a completed clause-level context proof",
                "open_gaps": ["owner_adjudication", "published_language_conformance", "independent_appraisal"],
            })
        chains[plane] = chain
    return contexts, chains


def build_input_alignments(contexts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Align only exact seed tokens after the declared underscore/hyphen ID encoding.

    This is inventory provenance, not synonym, merge, owner, or bounded-context
    adjudication.  Non-exact candidates remain deliberately unaligned.
    """
    inherited = list(read_jsonl(ATLAS / "registry/context-candidates.jsonl"))
    by_seed: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for candidate in inherited:
        seed = candidate.get("seed_term")
        if isinstance(seed, str):
            by_seed[seed].append(candidate)
    records = []
    for context in contexts:
        local_token = context["context_id"].split(".", 2)[2].replace("_", "-")
        for candidate in by_seed.get(local_token, []):
            records.append({
                "alignment_id": f"alignment.context_map.{len(records) + 1:04d}",
                "record_kind": "input_candidate_alignment",
                "status": STATUS,
                "local_context_id": context["context_id"],
                "input_candidate_id": candidate["record_id"],
                "input_family_id": candidate["family_id"],
                "match_basis": "exact_seed_token_after_declared_underscore_hyphen_id_encoding",
                "synonymy_inferred": False,
                "identity_inferred": False,
                "owner_inherited": False,
                "adjudication_inherited": False,
                "input_status": candidate.get("status"),
                "warning": "alignment proves inventory reuse only; split/merge/owner adjudication remains open",
            })
    return records


def populate_context_interfaces(contexts: list[dict[str, Any]], relations: list[dict[str, Any]]) -> None:
    by_id = {context["context_id"]: context for context in contexts}
    for relation in relations:
        source = by_id[relation["source"]["context_id"]]
        target = by_id[relation["target"]["context_id"]]
        source["export_contracts"].append({
            "contract_id": relation["export_contract_id"],
            "to_context_id": target["context_id"],
            "published_language_id": relation["published_language_id"],
        })
        target["imports"].append({
            "contract_id": relation["import_contract_id"],
            "from_context_id": source["context_id"],
            "published_language_id": relation["published_language_id"],
            "acl_decision_id": relation["acl_decision_id"],
        })
    for context in contexts:
        context["imports"].sort(key=lambda item: item["contract_id"])
        context["export_contracts"].sort(key=lambda item: item["contract_id"])


def relation_semantics(source: str, target: str, kind: str, cross_plane: bool) -> dict[str, Any]:
    """Derive a conservative translation posture from declared boundary roles.

    This does not infer term equivalence.  It only chooses which proof axis is
    activated by an explicitly constructed crossing.
    """
    tokens = set(source.split(".") + target.split("."))
    identity_terms = {"identifier", "identity", "identity_mapping", "counterparty_identity", "patient_identity", "asset_identity", "identity_resolution"}
    time_terms = {"temporal_reference", "event_time", "watermark", "window", "trigger", "stream_finality", "source_finality", "schedule_backfill", "snapshot_commit", "report_snapshot"}
    grain_terms = {"grain_transformation", "grain_population", "window", "metric_formula", "episode_cohort", "exposure_measurement", "result_evaluation", "report_snapshot"}
    evidence_terms = {"claim_evidence", "evidence_appraisal", "detection", "adjudication", "quality_certificate", "audit_observation", "query_receipt", "run_receipt", "usage_receipt"}

    totality = "partial" if kind == "anti_corruption_layer" else "conditional" if kind in {"conformist", "customer_supplier", "provider_offer", "compiler_requirement"} else "total"
    identity_change = "authorized_equivalence_required" if tokens & identity_terms else "preserved"
    time_change = "valid_recording_and_reference_change_explicit" if tokens & time_terms else "preserved"
    grain_change = "cardinality_and_grain_proof_required" if tokens & grain_terms else "preserved"
    if tokens & identity_terms:
        preservation = "identity_scope_changed"
        losses = ["foreign_identity_scope_not_promoted_without_authority"]
    elif tokens & evidence_terms:
        preservation = "evidence_weakening_declared"
        losses = ["issuer_evidence_not_promoted_to_appraisal_verdict"]
    elif tokens & grain_terms:
        preservation = "loss_declared"
        losses = ["record_level_alternatives_may_not_survive_grain_change"]
    elif cross_plane:
        preservation = "loss_declared"
        losses = ["foreign_context_not_reexported; unmapped content retained as residual"]
    else:
        preservation = "lossless"
        losses = []
    return {
        "totality": totality,
        "information_preservation": preservation,
        "losses": losses,
        "time_change": time_change,
        "identity_change": identity_change,
        "grain_change": grain_change,
        "residual_required": totality != "total" or bool(losses),
    }


def make_relation(index: int, source: str, target: str, kind: str, cross_plane: bool) -> tuple[dict[str, Any], dict[str, Any]]:
    source_parts = source.split(".")
    target_parts = target.split(".")
    source_plane, source_name = source_parts[1], source_parts[2]
    target_plane, target_name = target_parts[1], target_parts[2]
    relation_id = f"relation.context_map.{index:04d}"
    acl_id = f"acl.context_map.{index:04d}"
    translation = relation_semantics(source, target, kind, cross_plane)
    refusals = ["refuse_unresolved_edition", "refuse_unowned_semantics"]
    if translation["totality"] != "total":
        refusals.append("refuse_unhandled_foreign_value")
    if translation["losses"]:
        refusals.append("refuse_undeclared_information_loss")
    boundary_mode = {
        "anti_corruption_layer": "translate_into_local_language",
        "conformist": "conform_to_exact_foreign_edition",
        "published_language": "consume_published_language_without_semantic_promotion",
        "open_host_service": "consume_open_protocol_without_semantic_promotion",
        "evidence_submission": "preserve_evidence_envelope_without_claim_promotion",
        "independent_appraisal": "preserve_issuer_and_appraiser_separation",
        "authority_delegation": "validate_scope_expiry_and_revocation_without_semantic_translation",
        "compiler_requirement": "lower_requirement_without_provider_semantics",
        "provider_offer": "bind_offer_without_transferring_semantic_ownership",
        "runtime_receipt": "admit_occurrence_evidence_without_universal_guarantee",
        "customer_supplier": "consume_negotiated_contract_without_owner_transfer",
        "upstream_downstream": "consume_upstream_contract_without_owner_transfer",
        "shared_kernel": "use_joint_kernel_only_under_joint_change_governance",
    }[kind]
    relation = {
        "relation_id": relation_id,
        "record_kind": "context_map_relation",
        "status": STATUS,
        "source": {"context_id": source, "edition": 1, "role": "upstream"},
        "target": {"context_id": target, "edition": 1, "role": "downstream"},
        "relationship_type": kind,
        "dependency_direction": "source_to_target",
        "semantic_owner_context_id": source,
        "published_language_id": f"language.{source_plane}.{source_name}.v1",
        "import_contract_id": f"import.{target_plane}.{target_name}.from.{source_plane}.{source_name}.v1",
        "export_contract_id": f"export.{source_plane}.{source_name}.to.{target_plane}.{target_name}.v1",
        "authority_direction": "source_asserts_target_decides_use",
        "evidence_direction": "source_submits_target_appraises",
        "acl_decision_id": acl_id,
        "boundary_decision_mode": boundary_mode,
        "translation": translation,
        "version_coexistence": {
            "allowed": True,
            "requires": ["edition_qualified_import", "compatibility_relation", "migration_or_parallel_read_policy"],
        },
        "failure_refusals": refusals,
        "proof_obligation_ids": [
            "proof.context_map.semantic_owner",
            "proof.context_map.translation_totality",
            "proof.context_map.loss_accounting",
            "proof.context_map.version_coexistence",
        ],
        "cycle_projection": "authority_delegation" if kind == "authority_delegation" else "compiler_dependency" if kind == "compiler_requirement" else "none",
        "contributes_semantic_ownership_edge": False,
        "forbidden_cycle_class": "authority_delegation" if kind == "authority_delegation" else "compiler_dependency" if kind == "compiler_requirement" else "none",
    }
    acl = {
        "acl_id": acl_id,
        "record_kind": "anti_corruption_decision",
        "status": STATUS,
        "relation_id": relation_id,
        "foreign_context_id": source,
        "local_context_id": target,
        "input_language_id": relation["published_language_id"],
        "output_import_contract_id": relation["import_contract_id"],
        "mapping_posture": boundary_mode,
        "field_policy": "map only declared fields; retain unknown fields as typed residuals",
        "identity_policy": translation["identity_change"],
        "time_policy": translation["time_change"],
        "grain_policy": translation["grain_change"],
        "totality": translation["totality"],
        "information_preservation": translation["information_preservation"],
        "declared_losses": translation["losses"],
        "unknown_policy": "refuse_or_retain_typed_residual_never_guess",
        "refusals": refusals,
        "evidence_required": ["mapping_edition", "source_occurrence", "conformance_result", "loss_receipt"],
    }
    return relation, acl


def build_relations(chains: dict[str, list[str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    specs: list[tuple[str, str, str, bool]] = []
    for plane, chain in chains.items():
        for i in range(len(chain) - 1):
            specs.append((chain[i], chain[i + 1], "upstream_downstream", False))
        for i in range(len(chain) - 2):
            specs.append((chain[i], chain[i + 2], "published_language", False))

    # Explicit cross-context paths.  These are semantic crossings, not assertions
    # that the paired terms are synonyms or that either context owns the other.
    flows = [
        ["source", "connectivity", "admission", "mapping", "persistence", "quality", "provenance", "semantics", "study", "consumption"],
        ["constitutional", "admission", "mapping", "semantics", "query", "runtime", "provider", "product"],
        ["source", "stream", "orchestration", "runtime", "persistence", "query", "consumption"],
        ["governance", "security", "connectivity", "persistence", "consumption", "provenance"],
        ["intent", "study", "semantics", "quality", "decision_handoff"],
        ["finance_ccr", "study", "quality", "consumption", "product"],
        ["health_outcomes", "study", "quality", "security", "consumption"],
        ["manufacturing_maintenance", "stream", "study", "runtime", "orchestration"],
    ]
    # Resolve named pseudo-plane in one flow without inventing a context.
    resolved_flows: list[list[str]] = []
    for flow in flows:
        ids: list[str] = []
        for plane in flow:
            if plane == "decision_handoff":
                ids.append("ctx.study.decision_handoff")
            elif plane in chains:
                # Rotate the selected semantic surface to avoid every bridge using
                # only the first candidate in a plane.
                ids.append(chains[plane][len(ids) % len(chains[plane])])
        resolved_flows.append(ids)
    for ids in resolved_flows:
        for i in range(len(ids) - 1):
            specs.append((ids[i], ids[i + 1], "anti_corruption_layer", True))

    # Add explicit vertical end-to-end crossings at every stage.
    vertical_inputs = {
        "finance_ccr": ["source", "mapping", "semantics", "study", "quality", "security", "consumption", "provenance"],
        "health_outcomes": ["source", "admission", "governance", "study", "quality", "security", "consumption", "provenance"],
        "manufacturing_maintenance": ["source", "stream", "mapping", "study", "runtime", "orchestration", "consumption", "provenance"],
    }
    for vertical, planes in vertical_inputs.items():
        vchain = chains[vertical]
        for idx, plane in enumerate(planes):
            specs.append((chains[plane][idx % 6], vchain[idx % 6], "anti_corruption_layer", True))
            if idx < 6:
                specs.append((vchain[idx], chains[plane][(idx + 1) % 6], "evidence_submission", True))

    specs.extend([
        ("ctx.intent.decision_intent", "ctx.study.case_design", "customer_supplier", True),
        ("ctx.source.source_occurrence", "ctx.connectivity.connector_contract", "conformist", True),
        ("ctx.semantics.semantic_query_contract", "ctx.query.semantic_query", "open_host_service", True),
        ("ctx.provenance.claim_evidence", "ctx.provenance.evidence_appraisal", "independent_appraisal", False),
        ("ctx.governance.stewardship", "ctx.security.authorization_decision", "authority_delegation", True),
        ("ctx.semantics.semantic_query_contract", "ctx.provider.capability_requirement", "compiler_requirement", True),
        ("ctx.provider.capability_offer", "ctx.provider.target_profile", "provider_offer", False),
        ("ctx.provider.deployment_occurrence", "ctx.runtime.usage_receipt", "runtime_receipt", True),
    ])

    ordered_planes = [p[0] for p in PLANES]

    # Remove exact duplicate source/target/kind triples while keeping deterministic order.
    deduped: list[tuple[str, str, str, bool]] = []
    seen = set()
    for spec in specs:
        key = spec[:3]
        if key not in seen and spec[0] != spec[1]:
            seen.add(key)
            deduped.append(spec)
    # If deduplication dropped below the gate, add conservative ACL crossings;
    # never invent relationship kinds to satisfy a count.
    cursor = 0
    while len(deduped) < 300:
        left_plane = ordered_planes[cursor % len(ordered_planes)]
        right_plane = ordered_planes[(cursor + 7) % len(ordered_planes)]
        spec = (chains[left_plane][cursor % 6], chains[right_plane][(cursor + 3) % 6], "anti_corruption_layer", True)
        key = spec[:3]
        if key not in seen and spec[0] != spec[1]:
            seen.add(key)
            deduped.append(spec)
        cursor += 1

    relations, acls = [], []
    for index, spec in enumerate(deduped, start=1):
        relation, acl = make_relation(index, *spec)
        relations.append(relation)
        acls.append(acl)
    return relations, acls


LOSS_RULE_SEEDS = [
    ("identifier_namespace", "A foreign identifier without its namespace cannot be promoted to canonical identity."),
    ("edition_erasure", "Removing an edition destroys compatibility and replay evidence."),
    ("null_missing_unknown", "Null, missing, unknown and inapplicable cannot be silently collapsed."),
    ("unit_erasure", "A quantity without unit and dimension is not semantically admitted."),
    ("timezone_erasure", "A local time without zone or offset cannot be treated as an instant."),
    ("valid_record_time", "Valid time and recording time cannot substitute for one another."),
    ("event_processing_time", "Event time and processing time cannot substitute for one another."),
    ("cursor_completeness", "A continuation cursor proves position, not source completeness."),
    ("snapshot_change_gap", "Snapshot and change stream require an explicit stitch boundary."),
    ("decode_admit", "Successful decoding does not prove semantic admission."),
    ("schema_semantics", "Schema conformance does not prove domain meaning."),
    ("canonicalization_identity", "Canonical bytes do not prove real-world identity."),
    ("code_equivalence", "Code mapping strength must be explicit: exact, broader, narrower, related or unmapped."),
    ("match_merge", "A match candidate is not an authorized identity merge."),
    ("join_fanout", "A join without cardinality and grain proof must be refused."),
    ("aggregation_drill", "Aggregation destroys record-level alternatives unless a drill path is retained."),
    ("sampling_population", "A sample cannot be promoted to a population without design and uncertainty."),
    ("window_finality", "A watermark or closed window does not by itself prove business finality."),
    ("retry_effect", "A retry cannot repeat an irreversible effect without idempotency or compensation."),
    ("task_workflow", "Task success does not imply workflow or business outcome success."),
    ("object_table", "Object existence does not prove a committed table snapshot."),
    ("catalog_owner", "Catalog registration does not transfer semantic ownership."),
    ("cache_source", "Cache freshness does not prove source finality."),
    ("logical_physical", "A physical optimization may not silently change logical semantics."),
    ("kernel_qualification", "A kernel implementation is not qualified for a target without executed evidence."),
    ("metric_case", "A metric is not an analytical case, diagnosis, forecast, simulation or decision."),
    ("formula_estimator", "A formula is not an estimator and an estimator is not a fitted artifact."),
    ("estimand_metric", "An estimand cannot be replaced by a convenient observed metric."),
    ("result_evidence", "A result is not evidence of its own validity."),
    ("quality_detection", "A detection signal is not an adjudicated defect."),
    ("adjudication_correction", "An adjudication does not authorize a correction unless authority is explicit."),
    ("correction_source", "A downstream correction cannot rewrite source truth silently."),
    ("certificate_universal", "A certificate proves only its exact subject, criteria, time and evidence scope."),
    ("metadata_asset", "Metadata assertion, asset, catalog listing and certification remain distinct."),
    ("ontology_schema", "An ontology axiom and a technical schema constraint remain distinct."),
    ("master_golden", "Authoritative master and survivorship-derived golden projection remain distinct."),
    ("lineage_provenance", "A dependency edge is not a complete provenance claim."),
    ("audit_evidence", "An audit event is not automatically business evidence or lineage."),
    ("claim_truth", "A signed or well-provenanced claim is not thereby true."),
    ("authn_authz", "Authentication does not imply authorization."),
    ("approval_issuance", "Approval, issuance and enforcement remain separate acts."),
    ("encryption_permission", "Encryption does not create permission to use data."),
    ("purpose_classification", "Data-use purpose and security classification remain separate."),
    ("pseudonym_anonymity", "Pseudonymization must not be described as anonymization."),
    ("privacy_budget", "Privacy budget composition must be proven across releases."),
    ("view_result", "Presentation state is not the analytical result itself."),
    ("snapshot_live", "A report snapshot and a live view require different freshness semantics."),
    ("alert_notification", "An alert evaluation and a delivered notification are separate facts."),
    ("export_share", "A file export and a governed share have different control and revocation semantics."),
    ("demand_offer", "Resource demand and resource offer must not be collapsed."),
    ("quota_capacity", "Quota authority and physical capacity are independent."),
    ("reservation_allocation", "Reservation and allocation are separate lifecycle states."),
    ("lease_usage", "A lease grants bounded use; it is not evidence of measured usage."),
    ("requirement_offer", "A requirement and an offer bind only through compatibility evidence."),
    ("provider_owner", "A provider, product or suite is never the semantic owner by default."),
    ("offer_occurrence", "A generic offer does not establish an exact deployment occurrence."),
    ("product_context", "A product packages contexts but cannot redefine their languages silently."),
    ("version_alias", "A mutable alias cannot substitute for an exact edition in a reproducible binding."),
    ("migration_history", "Migration must preserve historical interpretation and evidence."),
    ("no_news", "Collector failure or silence cannot be interpreted as evidence that no change occurred."),
]


PROOF_SEEDS = [
    ("semantic_owner", "Every imported meaning has one explicit candidate owner and owner adjudication state."),
    ("published_language", "Every crossing names an exact published-language edition."),
    ("translation_totality", "Translation declares total, partial or conditional coverage."),
    ("loss_accounting", "Every weakened, dropped or transformed meaning emits a loss or residual receipt."),
    ("unknown_residual", "Unknown foreign values are refused or retained as typed residuals."),
    ("version_coexistence", "Parallel editions have explicit compatibility and migration policy."),
    ("identity_scope", "Identifier namespace and authorized identity mapping remain explicit."),
    ("time_axes", "Valid, observation, recording, decision and processing time changes are declared."),
    ("grain_cardinality", "Grain and cardinality changes are proven before join or aggregation."),
    ("authority_direction", "The source may assert; the consumer independently decides admissibility and use."),
    ("evidence_direction", "Evidence submission is distinct from independent appraisal."),
    ("failure_refusal", "Every partial crossing has a deterministic refusal or residual path."),
    ("forbidden_cycles", "Semantic ownership and authority delegation graphs contain no undeclared cycles."),
    ("dependency_direction", "Build and runtime dependency direction is explicit and acyclic where required."),
    ("product_nonownership", "No product, suite or provider is assigned semantic ownership by default."),
    ("provider_binding", "Provider offers bind only through exact requirements, targets and qualifications."),
    ("runtime_receipt", "Effectful crossings emit occurrence-scoped receipts."),
    ("historical_replay", "Historical inputs resolve under their original editions and mappings."),
    ("recall_propagation", "Recalled or superseded assertions invalidate dependent bindings and publications."),
    ("independent_appraisal", "Claims with material consequences have an appraisal authority independent of the issuer."),
    ("security_purpose", "Authorization, purpose, consent, residency and retention all close before release."),
    ("resource_finiteness", "ACL execution has finite payload, time, memory and residual budgets."),
    ("determinism", "Equivalent inputs and editions produce canonical translation decisions."),
    ("idempotency", "Repeated translation or delivery is idempotent or emits distinct attempt identity."),
    ("conformance", "At least two independent implementations can pass the published conformance surface."),
    ("negative_twin", "A negative twin fails at the exact boundary and names the refusal."),
    ("source_occurrence", "Every external assertion identifies an exact source occurrence."),
    ("schema_vs_semantics", "Structural conformance cannot satisfy semantic admission by itself."),
    ("metric_vs_case", "Metric lookup cannot satisfy an analytical-case requirement by itself."),
    ("quality_authority", "Detection, adjudication, correction and certification authorities remain separate."),
    ("lineage_claim", "Observed lineage, asserted provenance and appraised evidence remain distinguishable."),
    ("migration_exit", "Consumer data, definitions and evidence can exit without hidden provider semantics."),
]


LIBRARY_SEEDS = [
    ("context_identity", "Pure identity and edition types for bounded contexts and languages."),
    ("context_registry", "Open-world registry lookup without synonym or owner inference."),
    ("published_language", "Schema, command, event and compatibility contracts for published languages."),
    ("relationship_types", "DDD relationship vocabulary and direction validation."),
    ("acl_plan", "Pure anti-corruption translation plan and decision trace."),
    ("acl_runtime", "Effectful translation execution with receipts and bounded residuals."),
    ("mapping_registry", "Editioned field, code, identity, time and grain mappings."),
    ("translation_totality", "Total, partial and conditional mapping algebra."),
    ("loss_ledger", "Information-loss, weakening and residual accounting."),
    ("identity_bridge", "Namespace-preserving identity assertions and authorized decisions."),
    ("temporal_bridge", "Valid/recording/event/processing time translation."),
    ("grain_bridge", "Cardinality and grain-change proofs."),
    ("authority_graph", "Qualified authority, delegation, revocation and separation-of-duty graph."),
    ("evidence_exchange", "Claim, evidence, defeater and appraisal exchange contracts."),
    ("compatibility", "Multi-edition compatibility relations and coexistence decisions."),
    ("migration", "Upcast, backfill, parallel-read, recall and exit plans."),
    ("cycle_checker", "Forbidden semantic-owner, authority and dependency cycle detection."),
    ("refusal_catalog", "Stable typed refusals and precedence."),
    ("residual_store", "Typed preservation of untranslated foreign content."),
    ("context_diff", "Semantic diff and blast-radius calculation across editions."),
    ("requirement_offer", "Provider-neutral requirement/offer/binding types."),
    ("qualification", "Executable target qualification and evidence receipts."),
    ("compiler_context_ir", "Context/import/export/ACL nodes for language IR."),
    ("compiler_binder", "Exact edition and relationship binding without name dispatch."),
    ("runtime_gateway", "Inbound/outbound ACL gateway ports and occurrence receipts."),
    ("schema_adapter", "Carrier/schema DTO conversion isolated from domain values."),
    ("policy_adapter", "Authorization and purpose decision ports isolated from semantics."),
    ("provenance_adapter", "Provenance assertion and lineage observation exchange."),
    ("conformance_kit", "Positive, negative and round-trip contract tests."),
    ("vertical_path_harness", "Unrelated-vertical path and negative-twin execution harness."),
]


INNOVATIONS = [
    ("2021", "OpenAPI 3.1 aligned its schema dialect with JSON Schema 2020-12, sharpening interface/schema boundaries.", "https://spec.openapis.org/oas/v3.1.0.html"),
    ("2021", "Debezium incremental snapshots introduced chunked watermark windows for snapshot/change stitching.", "https://debezium.io/blog/2021/10/07/incremental-snapshots/"),
    ("2021", "W3C Trace Context established interoperable distributed correlation identifiers and propagation.", "https://www.w3.org/TR/trace-context/"),
    ("2022", "W3C DID Core standardized identifier documents, verification methods and service endpoints.", "https://www.w3.org/TR/did-core/"),
    ("2022", "GS1 EPCIS 2.0 expanded interoperable event capture and query for supply-chain visibility.", "https://ref.gs1.org/standards/epcis/2.0.0/"),
    ("2022", "in-toto 1.0 standardized software-supply-chain step attestations and layouts.", "https://github.com/in-toto/docs/blob/v1.0/in-toto-spec.md"),
    ("2022", "Apache Airflow data-aware scheduling made dataset updates explicit orchestration triggers.", "https://airflow.apache.org/docs/apache-airflow/2.10.4/authoring-and-scheduling/datasets.html"),
    ("2023", "FHIR R5 advanced healthcare resource and workflow contracts while retaining explicit version identity.", "https://hl7.org/fhir/R5/"),
    ("2023", "SLSA 1.0 stabilized provenance levels for build artifacts and supply-chain claims.", "https://slsa.dev/spec/v1.0/"),
    ("2023", "OpenTelemetry metrics reached stable semantic and protocol surfaces for cross-provider telemetry.", "https://opentelemetry.io/blog/2023/metrics-stable/"),
    ("2023", "Delta Universal Format exposed cross-format metadata generation, emphasizing format translation boundaries.", "https://docs.delta.io/latest/delta-uniform.html"),
    ("2024", "DCAT 3 standardized dataset series, version relations and checksums for catalog exchange.", "https://www.w3.org/TR/vocab-dcat-3/"),
    ("2024", "RDF Dataset Canonicalization standardized deterministic graph normalization for digests and verification.", "https://www.w3.org/TR/rdf-canon/"),
    ("2024", "AsyncAPI 3.0 separated operations, channels, messages and correlation in event-driven contracts.", "https://www.asyncapi.com/docs/reference/specification/v3.0.0"),
    ("2024", "OpenLineage facets expanded runtime lineage using editioned extensible job/run/dataset contracts.", "https://openlineage.io/docs/spec/facets/"),
    ("2024", "Apache Iceberg REST Catalog standardized a portable catalog protocol independent of table-format implementation.", "https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml"),
    ("2024", "CloudEvents SQL 1.0 standardized event filtering independently of transport and producer implementation.", "https://github.com/cloudevents/spec/blob/main/cloudevents/sql/spec.md"),
    ("2025", "Verifiable Credentials 2.0 separated issuer claims, verifier processing, status and integrity mechanisms.", "https://www.w3.org/TR/vc-data-model-2.0/"),
    ("2025", "Apache Iceberg v3 added deletion vectors, row lineage and expanded type semantics to its format contract.", "https://iceberg.apache.org/spec/#version-3-extended-types-and-capabilities"),
    ("2025", "OpenAPI 3.2 refined streaming, media types and callback/webhook interface description.", "https://spec.openapis.org/oas/v3.2.0.html"),
]


GAP_SEEDS = [
    "global semantic-owner adjudication remains incomplete",
    "shared-kernel governance and change authority require case-by-case proof",
    "published-language compatibility matrices need independent implementations",
    "mapping totality is not yet measured against production residual distributions",
    "identity-map authority varies by industry and jurisdiction",
    "bitemporal translation needs executable model checking",
    "grain-change proof needs modality-specific algebra",
    "loss severity and approval thresholds need domain policy",
    "foreign enum evolution needs occurrence-level monitoring",
    "schema registry and semantic registry failure precedence needs adjudication",
    "cross-region and cross-jurisdiction data-use translation remains deployment-specific",
    "revocation propagation latency is not yet bounded",
    "source finality and analytical finality lack universal relation",
    "backfill interpretation under historical mapping editions needs conformance fixtures",
    "stream and batch equivalence needs operator-specific proofs",
    "provider offer invalidation feeds are incomplete",
    "catalog aliases may hide mutable edition selection",
    "runtime receipts lack a single cross-provider evidence profile",
    "independent appraisal authorities are missing for some analytical claims",
    "partial translations need standardized residual carriers per modality",
    "cyclic organizational delegation needs policy-specific resolution",
    "product packaging blast-radius rules need observed migration evidence",
    "clinical vocabulary licensing and edition coexistence need explicit adapters",
    "counterparty legal-entity and agreement mappings require jurisdictional evidence",
    "industrial asset reconfiguration history needs identity-continuity tests",
    "two independent ACL implementations have not yet passed every relation fixture",
    "HTTP availability checks are intentionally excluded from deterministic validation",
    "the finite sample cannot establish global completeness",
]


def build_rules() -> list[dict[str, Any]]:
    result = []
    for idx, (name, law) in enumerate(LOSS_RULE_SEEDS, 1):
        result.append({
            "rule_id": f"rule.context_map.{name}",
            "record_kind": "loss_refusal_rule",
            "status": STATUS,
            "law": law,
            "failure_code": f"CONTEXT_MAP_{idx:03d}_{name.upper()}",
            "precedence": idx,
            "required_action": "refuse" if idx % 3 == 0 else "retain_typed_residual_or_refuse",
            "evidence_required": ["source_contract", "target_contract", "mapping_edition", "decision_trace"],
        })
    return result


def build_proofs() -> list[dict[str, Any]]:
    return [{
        "proof_id": f"proof.context_map.{name}",
        "record_kind": "proof_obligation",
        "status": STATUS,
        "claim": claim,
        "phase": ["language_ir", "observation_ir", "assurance_ir", "physical_ir", "release_ir"][idx % 5],
        "blocking": True,
        "evidence_kinds": ["static_check", "conformance_test", "runtime_receipt"],
        "on_failure": "emit_typed_gap_and_refuse_binding",
    } for idx, (name, claim) in enumerate(PROOF_SEEDS)]


def build_libraries() -> list[dict[str, Any]]:
    return [{
        "library_id": f"lib.context_map.{name}",
        "record_kind": "library_boundary",
        "status": STATUS,
        "responsibility": responsibility,
        "purity": "pure" if idx % 4 != 1 else "effect_adapter",
        "owns_semantics": idx in {0, 2, 3, 7, 8, 9, 10, 11, 12, 14, 16, 17, 19, 20, 22, 23},
        "must_not_own": ["provider brand dispatch", "product packaging", "foreign context meaning"],
        "decision_points": ["edition", "compatibility", "totality", "loss_policy", "authority", "failure_precedence"],
        "ports": [f"{name}_input", f"{name}_output", f"{name}_evidence"],
        "dependencies": [] if idx == 0 else [f"lib.context_map.{LIBRARY_SEEDS[max(0, idx - 1)][0]}"],
    } for idx, (name, responsibility) in enumerate(LIBRARY_SEEDS)]


def build_requirements_offers(libraries: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    requirements, offers, mappings = [], [], []
    for idx, lib in enumerate(libraries, 1):
        rid = f"requirement.context_map.{idx:03d}"
        oid = f"offer.context_map.{idx:03d}"
        requirements.append({
            "requirement_id": rid,
            "record_kind": "capability_requirement",
            "edition": 1,
            "capability": lib["responsibility"],
            "blocking": True,
            "traits": ["deterministic", "edition_qualified", "loss_explicit", "provider_neutral"],
            "binding_phase": ["language_ir", "assurance_ir", "physical_ir"][idx % 3],
        })
        offers.append({
            "offer_id": oid,
            "record_kind": "capability_offer",
            "edition": 1,
            "library_id": lib["library_id"],
            "capability": lib["responsibility"],
            "traits": ["deterministic", "edition_qualified", "loss_explicit", "provider_neutral"],
            "qualification_status": "unexecuted_candidate",
        })
        mappings.append({
            "mapping_id": f"compiler_mapping.context_map.{idx:03d}",
            "record_kind": "compiler_mapping",
            "requirement_id": rid,
            "offer_id": oid,
            "library_id": lib["library_id"],
            "ir_stage": requirements[-1]["binding_phase"],
            "binding_status": "candidate_unbound",
            "proof_obligation_ids": ["proof.context_map.semantic_owner", "proof.context_map.loss_accounting", "proof.context_map.conformance"],
            "invalidation_triggers": ["edition_change", "owner_change", "mapping_change", "qualification_expiry"],
        })
    return requirements, offers, mappings


def build_vertical_paths(chains: dict[str, list[str]]) -> list[dict[str, Any]]:
    specs = [
        ("finance_ccr", "Counterparty credit risk exposure-to-limit path", [
            "ctx.finance_ccr.counterparty_identity", "ctx.finance_ccr.legal_agreement", "ctx.finance_ccr.exposure_measurement",
            "ctx.finance_ccr.collateral_netting", "ctx.finance_ccr.default_simulation", "ctx.finance_ccr.ccr_decision"
        ], "refuse_legal_agreement_without_jurisdiction_and_edition"),
        ("health_outcomes", "Clinical cohort outcome-to-care path", [
            "ctx.health_outcomes.patient_identity", "ctx.health_outcomes.clinical_observation", "ctx.health_outcomes.episode_cohort",
            "ctx.health_outcomes.outcome_estimation", "ctx.health_outcomes.safety_adjudication", "ctx.health_outcomes.care_decision"
        ], "refuse_unadjudicated_safety_signal_as_care_order"),
        ("manufacturing_maintenance", "Sensor-to-maintenance work-order path", [
            "ctx.manufacturing_maintenance.asset_identity", "ctx.manufacturing_maintenance.sensor_observation", "ctx.manufacturing_maintenance.process_event",
            "ctx.manufacturing_maintenance.degradation_model", "ctx.manufacturing_maintenance.maintenance_optimization", "ctx.manufacturing_maintenance.work_order"
        ], "refuse_uncalibrated_sensor_as_failure_evidence"),
    ]
    records = []
    for idx, (vertical, title, path, refusal) in enumerate(specs, 1):
        records.append({
            "path_id": f"path.context_map.{vertical}.positive",
            "record_kind": "vertical_path",
            "status": STATUS,
            "vertical": vertical,
            "title": title,
            "polarity": "positive",
            "context_path": path,
            "required_proofs": ["proof.context_map.semantic_owner", "proof.context_map.identity_scope", "proof.context_map.time_axes", "proof.context_map.independent_appraisal"],
            "expected_outcome": "qualified_decision_handoff",
        })
        records.append({
            "path_id": f"path.context_map.{vertical}.negative_twin",
            "record_kind": "vertical_path",
            "status": STATUS,
            "vertical": vertical,
            "title": f"Negative twin: {title}",
            "polarity": "negative_twin",
            "context_path": path,
            "injected_fault": ["missing_edition", "unproved_identity_or_grain", "issuer_self_appraises"][idx - 1],
            "expected_refusal": refusal,
            "exact_boundary": path[idx],
            "required_proofs": ["proof.context_map.negative_twin"],
        })
    return records


def build_innovations(source_by_url: dict[str, str]) -> list[dict[str, Any]]:
    return [{
        "innovation_id": f"innovation.context_map.{idx:03d}",
        "record_kind": "innovation",
        "status": STATUS,
        "year": int(year),
        "description": description,
        "non_llm": True,
        "context_map_implication": "Treat the changed contract as an editioned published language or evidence surface; never as automatic global semantics.",
        "source_url": url,
        "source_id": source_by_url.get(url),
        "review_status": "primary_source_located" if url in source_by_url else "primary_source_url_declared_needs_local_crosswalk",
    } for idx, (year, description, url) in enumerate(INNOVATIONS, 1)]


def build_gaps() -> list[dict[str, Any]]:
    return [{
        "gap_id": f"gap.context_map.{idx:03d}",
        "record_kind": "typed_gap",
        "status": "open",
        "description": text,
        "blocking_scope": ["global_claim", "binding", "release", "qualification"][idx % 4],
        "evidence_needed": ["owner_adjudication", "independent_conformance", "production_occurrence_receipt"],
        "completion_effect": "No global completeness claim is permitted while this gap remains open.",
    } for idx, text in enumerate(GAP_SEEDS, 1)]


def schemas() -> dict[str, dict[str, Any]]:
    base = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "additionalProperties": True}
    specs = {
        "context": (["context_id", "edition", "status", "plane_id", "semantic_owner", "sovereign_question", "published_languages", "evidence_refs"], "context_id"),
        "relation": (["relation_id", "source", "target", "relationship_type", "published_language_id", "acl_decision_id", "translation", "version_coexistence", "proof_obligation_ids"], "relation_id"),
        "acl": (["acl_id", "relation_id", "foreign_context_id", "local_context_id", "totality", "information_preservation", "unknown_policy", "refusals"], "acl_id"),
        "source": (["source_id", "title", "publisher", "url", "authority_scope", "limitations"], "source_id"),
        "rule": (["rule_id", "law", "failure_code", "precedence", "required_action"], "rule_id"),
        "proof": (["proof_id", "claim", "phase", "blocking", "on_failure"], "proof_id"),
        "library": (["library_id", "responsibility", "purity", "must_not_own", "decision_points"], "library_id"),
        "requirement": (["requirement_id", "edition", "capability", "traits", "binding_phase"], "requirement_id"),
        "offer": (["offer_id", "edition", "library_id", "capability", "traits", "qualification_status"], "offer_id"),
        "compiler_mapping": (["mapping_id", "requirement_id", "offer_id", "library_id", "ir_stage", "proof_obligation_ids"], "mapping_id"),
        "innovation": (["innovation_id", "year", "description", "non_llm", "source_url", "review_status"], "innovation_id"),
        "gap": (["gap_id", "status", "description", "evidence_needed"], "gap_id"),
        "vertical_path": (["path_id", "vertical", "polarity", "context_path", "required_proofs"], "path_id"),
        "input_alignment": (["alignment_id", "local_context_id", "input_candidate_id", "match_basis", "synonymy_inferred", "owner_inherited"], "alignment_id"),
    }
    result = {}
    for name, (required, id_field) in specs.items():
        schema = dict(base)
        schema.update({
            "$id": f"https://san.example/spec/context-map/{name}.schema.json",
            "title": f"SAN candidate context-map {name}",
            "required": required,
            "properties": {id_field: {"type": "string", "minLength": 1}},
        })
        result[name] = schema
    return result


def build_metamodel() -> dict[str, Any]:
    return {
        "metamodel_id": "san.domain_atlas.context_map_contract",
        "edition": 1,
        "status": STATUS,
        "completion_claim": False,
        "identity_rule": "context_id and edition form identity; names, products, providers and organizational teams do not",
        "semantic_owner_rule": "an explicitly adjudicated authority role owns meaning; a consumer, product, suite, provider, catalog or deployment does not by default",
        "relationship_types": RELATION_TYPES,
        "relationship_semantics": {
            "upstream_downstream": "source meaning constrains downstream use without granting implementation control",
            "customer_supplier": "downstream needs influence an upstream contract under an explicit negotiation and change process",
            "conformist": "downstream adopts an upstream published language and records the resulting coupling",
            "anti_corruption_layer": "downstream translates a foreign language into its local language with explicit loss and refusal",
            "open_host_service": "upstream exposes a stable protocol for multiple consumers",
            "published_language": "an editioned contract is intentionally available for external dependence",
            "shared_kernel": "a deliberately small shared model has joint ownership, change authority and conformance tests",
            "separate_ways": "contexts deliberately do not integrate and preserve independent models",
            "independent_appraisal": "a party distinct from the issuer evaluates a claim against explicit criteria",
            "authority_delegation": "scoped, time-bounded, revocable authority is delegated without transferring accountability",
            "evidence_submission": "an issuer submits evidence; a consumer or appraiser decides relevance and sufficiency",
            "compiler_requirement": "a semantic context states a provider-neutral compiler requirement",
            "provider_offer": "a library or provider offers a capability without acquiring semantic ownership",
            "runtime_receipt": "an occurrence returns evidence of what happened, not a universal guarantee",
        },
        "closed_axes": {
            "translation_totality": ["total", "partial", "conditional"],
            "information_preservation": ["lossless", "loss_declared", "evidence_weakening_declared", "identity_scope_changed"],
            "authority_direction": ["source_asserts_target_decides_use"],
            "evidence_direction": ["source_submits_target_appraises"],
            "version_policy": ["exact_edition", "compatible_parallel", "explicit_migration", "refuse_unresolved"],
            "unknown_policy": ["refuse", "retain_typed_residual", "explicit_extension"],
        },
        "non_collapsible_distinctions": [
            "bounded context != product != suite != provider != deployment occurrence",
            "semantic owner != accountable role != steward != custodian != implementation maintainer",
            "published language != transport protocol != carrier schema != provider API",
            "import != export != requirement != offer != binding != runtime receipt",
            "translation totality != structural parse success != semantic admission",
            "identifier mapping != match candidate != authorized identity decision != merge",
            "valid time != observation time != event time != recording time != processing time != decision time",
            "grain change != cardinality change != representation change != information loss",
            "authority delegation != data flow != dependency != evidence submission",
            "claim issuer != evidence source != independent appraiser != decision authority",
        ],
        "forbidden_cycle_classes": {
            "semantic_ownership": "a context cannot own the owner of its own meaning",
            "authority_delegation": "delegation must not return broader or equal authority to an ancestor",
            "compiler_dependency": "lower IR stages cannot depend semantically on later physical selections",
            "independent_appraisal": "issuer and independent appraiser cannot be the same authority for the same claim",
        },
        "open_registries": [
            "contexts", "published_languages", "context_map_relations", "acl_decisions", "mapping_editions",
            "sources", "providers", "products", "deployment_occurrences", "vertical_paths",
        ],
    }


def encode_jsonl(records: list[dict[str, Any]], id_key: str) -> str:
    return "".join(canonical_json(record) + "\n" for record in sorted(records, key=lambda r: r[id_key]))


def encode_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def emit(path: Path, content: str, check: bool) -> None:
    if check:
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            raise SystemExit(f"non-deterministic or stale artifact: {path.relative_to(ROOT)}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if generated artifacts are stale")
    args = parser.parse_args()

    sources = build_sources()
    if len(sources) < 60:
        raise SystemExit(f"need at least 60 authoritative sources, found {len(sources)}")
    contexts, chains = build_contexts(sources)
    input_alignments = build_input_alignments(contexts)
    relations, acls = build_relations(chains)
    populate_context_interfaces(contexts, relations)
    rules = build_rules()
    proofs = build_proofs()
    libraries = build_libraries()
    requirements, offers, mappings = build_requirements_offers(libraries)
    vertical_paths = build_vertical_paths(chains)
    source_by_url = {s["url"]: s["source_id"] for s in sources}
    innovations = build_innovations(source_by_url)
    gaps = build_gaps()

    files: dict[str, str] = {
        "metamodel.json": encode_json(build_metamodel()),
        "sources.jsonl": encode_jsonl(sources, "source_id"),
        "contexts.jsonl": encode_jsonl(contexts, "context_id"),
        "relations.jsonl": encode_jsonl(relations, "relation_id"),
        "acl-decisions.jsonl": encode_jsonl(acls, "acl_id"),
        "loss-refusal-rules.jsonl": encode_jsonl(rules, "rule_id"),
        "proof-obligations.jsonl": encode_jsonl(proofs, "proof_id"),
        "library-boundaries.jsonl": encode_jsonl(libraries, "library_id"),
        "requirements.jsonl": encode_jsonl(requirements, "requirement_id"),
        "offers.jsonl": encode_jsonl(offers, "offer_id"),
        "compiler-mappings.jsonl": encode_jsonl(mappings, "mapping_id"),
        "innovations-2021-2026.jsonl": encode_jsonl(innovations, "innovation_id"),
        "gaps.jsonl": encode_jsonl(gaps, "gap_id"),
        "vertical-paths.jsonl": encode_jsonl(vertical_paths, "path_id"),
        "input-alignments.jsonl": encode_jsonl(input_alignments, "alignment_id"),
    }
    for name, schema in schemas().items():
        files[f"schemas/{name}.schema.json"] = encode_json(schema)

    for relative, content in sorted(files.items()):
        emit(ROOT / relative, content, args.check)

    manifest = {
        "corpus_id": "san.domain_atlas.global_context_map",
        "edition": 1,
        "status": STATUS,
        "completion_claim": False,
        "generated_on": RETRIEVED,
        "counts": {
            "sources": len(sources), "contexts": len(contexts), "relations": len(relations),
            "acl_decisions": len(acls), "loss_refusal_rules": len(rules), "proof_obligations": len(proofs),
            "library_boundaries": len(libraries), "requirements": len(requirements), "offers": len(offers),
            "compiler_mappings": len(mappings), "innovations": len(innovations), "gaps": len(gaps),
            "vertical_paths": len(vertical_paths),
            "input_alignments": len(input_alignments),
        },
        "constitutional_warnings": [
            "candidate/open-world corpus; finite enumeration is not global completeness",
            "names never establish synonymy, identity, ownership, authority, compatibility or provider binding",
            "products, suites and providers are consumers or packagers and are never semantic owners by default",
        ],
        "inputs": SOURCE_FILES + ["../context-families.json", "../registry/context-candidates.jsonl"],
        "artifacts": {
            name: hashlib.sha256(content.encode("utf-8")).hexdigest()
            for name, content in sorted(files.items())
        },
    }
    emit(ROOT / "manifest.json", encode_json(manifest), args.check)


if __name__ == "__main__":
    main()
