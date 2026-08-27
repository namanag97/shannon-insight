#!/usr/bin/env python3
"""Build an evidence-backed semantic slice for deterministic process analytics."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SEM = HERE.parent
REGISTRY = SEM.parents[1]
AS_OF = "2026-08-27"

AXES = [
    "semantic_object", "semantic_role", "identity_and_equality", "grain_and_cardinality",
    "state_and_change", "time", "order_and_topology", "partiality_and_uncertainty",
    "authority_and_trust", "effect_boundary", "representation", "composition_algebra",
    "compatibility_and_evolution", "resources_and_failure", "evidence_and_conformance",
    "privacy_security_safety",
]

LIBRARIES = [
    "library.method_kernels.process_case_projection",
    "library.method_kernels.process_conformance_methods",
    "library.method_kernels.process_discovery_methods",
    "library.method_kernels.process_event_projection",
    "library.method_kernels.process_methods",
    "library.method_kernels.process_performance_methods",
    "library.method_kernels.process_state_aware_projection",
    "library.method_kernels.process_temporal_graph_projection",
]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def slug(value: str) -> str:
    return value.replace("_", "-").replace(".", "-")


def sources() -> list[dict[str, Any]]:
    return [
        {"source_id":"source.process.ieee-xes-2023","title":"IEEE 1849-2023 — eXtensible Event Stream (XES)","authors_or_publisher":["IEEE Standards Association","XES Working Group"],"year":2023,"source_kind":"active_standard","url":"https://standards.ieee.org/ieee/1849/10907/","bounded_implication":"XES defines an interoperable event-log/event-stream carrier grammar and extension mechanism.","authority_limit":"A carrier standard does not choose a domain case notion, process truth, analytical method, state semantics or acceptance criterion."},
        {"source_id":"source.process.ocel-2.0","title":"OCEL 2.0 Specification","authors_or_publisher":["Alessandro Berti","Istvan Koren","Jan Niklas Adams","Gyunam Park","Wil M. P. van der Aalst","OCEL Standard"],"year":2024,"source_kind":"official_specification_and_paper","url":"https://ocel-standard.org/specification/overview/","bounded_implication":"OCEL 2.0 represents events, typed objects, qualified event-object and object-object relations, changing object attributes and multiple exchange formats.","authority_limit":"OCEL is an exchange representation; it does not make every relation causal, define operational states, select a leading object, or prove an analysis valid."},
        {"source_id":"source.process.oced-core-2024","title":"Towards a Simple and Extensible Standard for Object-Centric Event Data — Core Model, Design Space, and Lessons Learned","authors_or_publisher":["Dirk Fahland","Marco Montali","Julian Lebherz","Wil M. P. van der Aalst","OCED community"],"year":2024,"source_kind":"primary_research_and_community_design_report","url":"https://arxiv.org/abs/2410.14495","bounded_implication":"OCED separates a reliable core model from conventions and extensions and documents trade-offs across independently implemented object-centric event-data models.","authority_limit":"The proposal and design space do not ratify one SAN representation or erase use-case-specific conventions, extensions and semantic headers."},
        {"source_id":"source.process.ekg-fahland-2022","title":"Process Mining over Multiple Behavioral Dimensions with Event Knowledge Graphs","authors_or_publisher":["Dirk Fahland","Eindhoven University of Technology"],"year":2022,"source_kind":"peer_reviewed_open_access_book_chapter","url":"https://research.tue.nl/en/publications/process-mining-over-multiple-behavioral-dimensions-with-event-kno/","bounded_implication":"Event knowledge graphs explicitly represent entities, infer entity-scoped directly-follows relations and permit provenance-preserving aggregation of behavioral structures.","authority_limit":"Graph construction and aggregation do not prove causal relations, completeness, a unique case, or decision authority; dynamic relationships and property changes require additional semantics."},
        {"source_id":"source.process.tekg-2024","title":"Transforming Object-Centric Event Logs to Temporal Event Knowledge Graphs","authors_or_publisher":["Shahrzad Khayatbashi","Olaf Hartig","Amin Jalali"],"year":2024,"source_kind":"peer_reviewed_research_with_reference_artifacts","url":"https://arxiv.org/abs/2406.07596","bounded_implication":"tEKG formalizes a temporal graph projection from OCEL 2.0 that preserves time-varying object attributes through entity snapshots and temporal relationships.","authority_limit":"A transformation algorithm does not establish domain state meaning, causal direction, source completeness or equivalence to every event-knowledge-graph model."},
        {"source_id":"source.process.sa-ocpm-2025","title":"State-Aware Object-Centric Process Mining: Enhancing OCEL 2.0 with Explicit State Transitions","authors_or_publisher":["Dina Kretzschmann","Alessandro Berti","Wil M. P. van der Aalst"],"year":2025,"source_kind":"peer_reviewed_research","url":"https://www.alessandroberti.it/new_papers/2025_Dina_SAOCPM.pdf","bounded_implication":"SA-OCPM derives explicit object-state-transition events and state-aware event labels from a declared leading object type and state model.","authority_limit":"State definitions are domain-specific; derived states and enriched events are analytical projections, not source events or operational authorization."},
        {"source_id":"source.process.dynamic-relations-2026","title":"Detecting Dynamic Relationships in Object-Centric Event Logs","authors_or_publisher":["Alessandro Gianola","Zeeshan Hameed","Marco Montali","Anjo Seidel","Mathias Weske","Sarah Winkler"],"year":2026,"source_kind":"research_preprint","url":"https://arxiv.org/abs/2604.13053","bounded_implication":"The work identifies explicit assumptions needed for semantically unambiguous dynamic object relationships in OCELs.","authority_limit":"A recent preprint is an innovation candidate, not a ratified standard or universal relationship semantics."},
        {"source_id":"source.process.discovery","title":"Process Discovery","authors_or_publisher":["IEEE Task Force on Process Mining community"],"year":2024,"source_kind":"official_community_technical_resource","url":"https://www.processmining.org/process-discovery.html","bounded_implication":"Process discovery constructs a process-model candidate from recorded event behavior for subsequent analysis.","authority_limit":"A discovered model describes evidence under a method and configuration; it is not the governing process specification or proof of fitness."},
        {"source_id":"source.process.conformance","title":"Conformance Checking","authors_or_publisher":["IEEE Task Force on Process Mining community"],"year":2024,"source_kind":"official_community_technical_resource","url":"https://www.processmining.org/conformance.html","bounded_implication":"Conformance compares observed behavior with a process model; token replay and alignments have distinct guarantees and costs.","authority_limit":"Fitness, precision or an optimal alignment is scoped to a model, mapping, cost function and log cut; none alone proves compliance, cause or authorization."},
        {"source_id":"source.process.pm-spectrum","title":"Process Mining: Data Science in Action and task taxonomy","authors_or_publisher":["Wil M. P. van der Aalst","ProcessMining.org"],"year":2016,"source_kind":"foundational_book_and_official_resource","url":"https://processmining.org/old-version/book.html","bounded_implication":"The process-mining spectrum separates discovery, conformance, organizational/time perspectives, operational support and predictive analysis.","authority_limit":"A field taxonomy does not merge these methods into one algorithm or confer domain decision authority."},
    ]


def modules() -> list[dict[str, Any]]:
    return [
        {"module_id":"module.process.event-data-carrier","question":"How is event data interchanged without claiming its domain interpretation?","formalism":"editioned carrier/schema","source_refs":["source.process.ieee-xes-2023","source.process.ocel-2.0"],"imports":[],"exports":["typed event/object carrier view","validation losses"],"owned_by":"context.process-event-data-representation"},
        {"module_id":"module.process.oced-semantic-core","question":"What events, objects, types and qualified relations constitute the admitted object-centric event-data graph?","formalism":"typed relational graph with temporal attributes","source_refs":["source.process.ocel-2.0","source.process.oced-core-2024"],"imports":["module.process.event-data-carrier"],"exports":["object-centric event-data view","semantic-header vacancies"],"owned_by":"context.object-centric-event-data"},
        {"module_id":"module.process.case-projection","question":"Which declared perspective projects multi-object behavior into cases, and what information is lost?","formalism":"typed projection with loss algebra","source_refs":["source.process.ocel-2.0","source.process.ekg-fahland-2022"],"imports":["module.process.oced-semantic-core"],"exports":["case projection","projection-loss report"],"owned_by":"context.process-projection"},
        {"module_id":"module.process.event-knowledge-graph","question":"How are entity-scoped behavioral relations and provenance-preserving aggregates represented?","formalism":"event knowledge graph","source_refs":["source.process.ekg-fahland-2022"],"imports":["module.process.oced-semantic-core"],"exports":["event knowledge graph","entity-scoped directly-follows paths","aggregation provenance"],"owned_by":"context.process-projection"},
        {"module_id":"module.process.temporal-event-knowledge-graph","question":"How are attribute changes and temporal entity snapshots preserved in a graph projection?","formalism":"temporal property graph transformation","source_refs":["source.process.tekg-2024","source.process.dynamic-relations-2026"],"imports":["module.process.oced-semantic-core","module.process.event-knowledge-graph"],"exports":["temporal EKG","graph-projection loss"],"owned_by":"context.process-projection"},
        {"module_id":"module.process.state-aware-projection","question":"How does an authorized domain state model derive object states, transitions and perspective-dependent state-aware events?","formalism":"state function plus derived-event projection","source_refs":["source.process.ocel-2.0","source.process.sa-ocpm-2025"],"imports":["module.process.oced-semantic-core"],"exports":["state-aware event view","derived transition events","state derivation evidence"],"owned_by":"context.process-state-projection"},
        {"module_id":"module.process.discovery","question":"Which process-model candidate is discovered from a declared event view, method and configuration?","formalism":"process discovery algorithm contract","source_refs":["source.process.discovery","source.process.pm-spectrum"],"imports":["module.process.case-projection"],"exports":["discovered process model","discovery diagnostics"],"owned_by":"context.process-discovery"},
        {"module_id":"module.process.conformance","question":"How is an admitted event view compared with an admitted model under an explicit mapping and cost/metric profile?","formalism":"replay/alignment relation and metric algebra","source_refs":["source.process.conformance","source.process.pm-spectrum"],"imports":["module.process.case-projection"],"exports":["alignment","scoped fitness/precision results","deviation findings"],"owned_by":"context.process-conformance"},
        {"module_id":"module.process.performance","question":"How are durations, waits, queues, handoffs and bottleneck candidates measured at a declared grain and time semantics?","formalism":"temporal measurement and aggregation algebra","source_refs":["source.process.ekg-fahland-2022","source.process.pm-spectrum"],"imports":["module.process.case-projection","module.process.event-knowledge-graph"],"exports":["performance measures","bottleneck candidates","measurement uncertainty"],"owned_by":"context.process-performance"},
        {"module_id":"module.process.finding-handoff","question":"How does a process-analysis result remain a scoped, non-authoritative finding?","formalism":"claim-evidence-residual envelope","source_refs":["source.process.conformance","source.process.pm-spectrum"],"imports":["module.process.discovery","module.process.conformance","module.process.performance"],"exports":["analytical finding","assumption and residual ledger","decision handoff"],"owned_by":"context.analytical-finding"},
    ]


LIBRARY_MODULES = {
    "library.method_kernels.process_case_projection":["module.process.case-projection"],
    "library.method_kernels.process_conformance_methods":["module.process.conformance","module.process.finding-handoff"],
    "library.method_kernels.process_discovery_methods":["module.process.discovery","module.process.finding-handoff"],
    "library.method_kernels.process_event_projection":["module.process.oced-semantic-core","module.process.event-knowledge-graph"],
    "library.method_kernels.process_methods":["module.process.discovery","module.process.conformance","module.process.performance","module.process.finding-handoff"],
    "library.method_kernels.process_performance_methods":["module.process.performance","module.process.finding-handoff"],
    "library.method_kernels.process_state_aware_projection":["module.process.state-aware-projection"],
    "library.method_kernels.process_temporal_graph_projection":["module.process.temporal-event-knowledge-graph"],
}


def non_collapse_laws() -> list[dict[str, Any]]:
    laws = [
        ("carrier-is-not-semantic-event-data","A valid XES/OCEL document is not proof that its events, objects, qualifiers or attributes have the intended domain meaning.",["source.process.ieee-xes-2023","source.process.ocel-2.0"]),
        ("object-is-not-case","An object identity or type is not an inherent process case; a case is a declared projection with loss.",["source.process.ocel-2.0","source.process.ekg-fahland-2022"]),
        ("event-order-is-not-causality","Timestamp or directly-follows order does not by itself establish causal influence.",["source.process.ekg-fahland-2022"]),
        ("relation-is-not-static","An object-object relation without temporal semantics cannot represent every dynamic relationship unambiguously.",["source.process.dynamic-relations-2026","source.process.tekg-2024"]),
        ("attribute-change-is-not-state-transition","A changed attribute becomes a state transition only under a declared domain state function and leading-object perspective.",["source.process.sa-ocpm-2025"]),
        ("derived-event-is-not-source-event","A generated state-transition event or aggregate process event must retain derivation provenance and cannot rewrite the source log.",["source.process.sa-ocpm-2025","source.process.ekg-fahland-2022"]),
        ("ocel-is-not-oced-totality","OCEL is an exchange format within the broader OCED design space; conventions and extensions remain explicit.",["source.process.oced-core-2024"]),
        ("oced-is-not-ekg","Object-centric event-data semantics and an event-knowledge-graph analytical projection have different identities and compatibility rules.",["source.process.oced-core-2024","source.process.ekg-fahland-2022"]),
        ("ekg-is-not-tekg","An EKG without temporal entity-snapshot semantics is not equivalent to a tEKG.",["source.process.tekg-2024"]),
        ("discovered-model-is-not-governing-model","A discovered model is a method/configuration-scoped finding, not the authoritative intended process.",["source.process.discovery"]),
        ("fitness-is-not-compliance","Conformance fitness or an alignment does not alone prove legal, policy or control compliance.",["source.process.conformance"]),
        ("token-replay-is-not-alignment","Token replay and optimal alignment have different completeness, optimality and resource contracts.",["source.process.conformance"]),
        ("bottleneck-is-not-root-cause","A measured queue or delay concentration is a bottleneck candidate, not a causal diagnosis.",["source.process.ekg-fahland-2022","source.process.pm-spectrum"]),
        ("finding-is-not-authority","No process-mining result may authorize a mutation, accuse a person or waive a control without an external decision authority.",["source.process.pm-spectrum"]),
        ("projection-equality-is-not-source-equality","Two equal projected traces or graphs need not preserve equal source histories, objects or relations.",["source.process.ekg-fahland-2022","source.process.tekg-2024"]),
        ("state-label-is-perspective-dependent","The same event can carry different state-aware meanings for different leading objects.",["source.process.sa-ocpm-2025"]),
        ("missing-event-is-not-no-event","Absence in an admitted event cut cannot prove that no world event occurred.",["source.process.ieee-xes-2023","source.process.ocel-2.0"]),
        ("one-format-is-not-one-meaning","JSON, XML, SQLite and other carriers are equivalent only under an explicit semantic round-trip and loss profile.",["source.process.ocel-2.0"]),
    ]
    return [{"law_id":f"law.process.{name}","statement":statement,"source_refs":refs,"status":"EVIDENCE_BACKED_CANDIDATE_OWNER_UNRATIFIED","completion_claim":False} for name,statement,refs in laws]


def methods() -> list[dict[str, Any]]:
    rows = [
        ("event-data-validation","preparation","event carrier","validated carrier plus loss report","representation correctness only"),
        ("object-centric-event-normalization","preparation","source event/object records","OCED/OCEL semantic view","source-to-semantic mapping authority required"),
        ("case-projection","projection","multi-object event view","case/event-log view plus projection loss","chosen case perspective only"),
        ("object-centric-projection","projection","OCED/OCEL view","object-centric analytical view","no unique case implied"),
        ("event-knowledge-graph-projection","projection","event/entity view","EKG plus provenance","behavioral edges are scoped relations, not causes"),
        ("temporal-ekg-projection","projection","OCEL 2.0 view","tEKG plus temporal loss report","snapshot and relation-time policy explicit"),
        ("state-aware-projection","projection","event/object view plus state model","state-aware events/transitions","domain state authority remains external"),
        ("control-flow-discovery","discovery","admitted event view","process-model candidate","method/configuration-scoped finding"),
        ("object-centric-discovery","discovery","object-centric event view","object-centric process-model candidate","perspective and convergence/divergence preserved"),
        ("variant-and-pattern-discovery","discovery","projected executions or graph segments","variants/pattern candidates","equivalence and support threshold explicit"),
        ("token-replay","conformance","log, model and mapping","replay result","heuristic/local choices declared"),
        ("optimal-alignment","conformance","log, model, mapping and cost profile","alignment and deviations","optimal only for declared search/cost semantics"),
        ("fitness-precision-generalization","evaluation","log/model relation","scoped quality measures","dimensions never collapsed into one truth score"),
        ("compliance-checking","conformance","observations, normative model and authority profile","candidate violations/evidence","finding is not legal/control verdict"),
        ("duration-waiting-service-time","performance","ordered event/object observations","temporal measures","clock, interval and censoring semantics explicit"),
        ("queue-handoff-resource-analysis","performance","events, actors/resources and relations","queue/handoff measures","actor correlation is not culpability"),
        ("bottleneck-detection","diagnostic","performance measures and comparison profile","bottleneck candidates","not root cause"),
        ("comparative-process-analysis","comparative","two or more admitted cuts/models","difference findings","population, projection and metric equivalence required"),
        ("drift-change-analysis","diagnostic","time-indexed behavior/model windows","change candidates","windowing and multiplicity control explicit"),
        ("process-root-cause-handoff","diagnostic_handoff","deviations and contextual evidence","diagnostic hypothesis","requires separate causal/refutation method before causal claim"),
    ]
    return [{"method_id":f"method.process.{name}","method_class":klass,"input_semantics":inp,"output_semantics":out,"authority_limit":limit,"status":"RESEARCHED_METHOD_BOUNDARY_CANDIDATE"} for name,klass,inp,out,limit in rows]


def expert_profiles() -> list[dict[str, Any]]:
    return [
        {"expert_id":"expert.process.dirk-fahland","name":"Dirk Fahland","contribution_refs":["source.process.ekg-fahland-2022","source.process.oced-core-2024"],"learnable_design_laws":["Do not force multi-entity behavior into one inherent case.","Keep entity-scoped directly-follows paths and aggregation provenance explicit.","Treat OCED construction, semantic depth and graph/query layers as separate decisions."],"authority_limit":"Expert work constrains candidates; it does not make the author SAN's semantic owner."},
        {"expert_id":"expert.process.wil-van-der-aalst","name":"Wil M. P. van der Aalst","contribution_refs":["source.process.ocel-2.0","source.process.sa-ocpm-2025","source.process.pm-spectrum"],"learnable_design_laws":["Separate discovery, conformance, enhancement and operational support.","Preserve object-centric relations rather than manufacturing a single case identifier.","Make analysis perspective and method assumptions explicit."],"authority_limit":"Foundational scholarship is evidence, not enterprise decision authority."},
        {"expert_id":"expert.process.marco-montali","name":"Marco Montali","contribution_refs":["source.process.oced-core-2024","source.process.dynamic-relations-2026"],"learnable_design_laws":["Separate a stable event-data core from conventions and extensions.","Dynamic relationships need explicit temporal assumptions.","Do not standardize ambiguous constructs merely because implementations can encode them."],"authority_limit":"Research participation does not ratify SAN contracts."},
        {"expert_id":"expert.process.alessandro-berti","name":"Alessandro Berti","contribution_refs":["source.process.ocel-2.0","source.process.sa-ocpm-2025"],"learnable_design_laws":["Keep exchange-format validation executable across carriers.","Model state-aware enrichment as a derived projection with a declared leading object and state function.","Retain reproducible fixtures and transformation artifacts."],"authority_limit":"Implementations and papers do not own downstream domain state definitions."},
        {"expert_id":"expert.process.dina-kretzschmann","name":"Dina Kretzschmann","contribution_refs":["source.process.sa-ocpm-2025"],"learnable_design_laws":["Make object states and transitions explicit when diagnostics depend on them.","Distinguish a transition event from an ordinary event enriched with state context.","State meaning remains domain-specific and perspective-dependent."],"authority_limit":"The method does not select an enterprise's states or thresholds."},
        {"expert_id":"expert.process.shahrzad-khayatbashi","name":"Shahrzad Khayatbashi","contribution_refs":["source.process.tekg-2024"],"learnable_design_laws":["Preserve changing object attributes through temporal entity snapshots.","Specify OCEL-to-graph transformation semantics and modes.","Record projection loss instead of treating graph conversion as identity."],"authority_limit":"A tEKG transformation is one qualified representation, not universal graph semantics."},
        {"expert_id":"expert.process.olaf-hartig","name":"Olaf Hartig","contribution_refs":["source.process.tekg-2024"],"learnable_design_laws":["Temporal graph semantics belong in the model, not only timestamp properties.","Separate data transformation correctness from analytical interpretation.","Version graph representations and transformation laws independently."],"authority_limit":"Temporal-graph expertise does not confer process or operational authority."},
        {"expert_id":"expert.process.josep-carmona","name":"Josep Carmona","contribution_refs":["source.process.conformance"],"learnable_design_laws":["Distinguish heuristic replay from exhaustive/optimal alignment.","Bind conformance outcomes to a specific model, mapping and cost profile.","Expose computational trade-offs and typed incompleteness."],"authority_limit":"A conformance algorithm does not decide compliance or sanctions."},
    ]


def innovations() -> list[dict[str, Any]]:
    rows = [
        ("multi-dimensional-event-knowledge-graphs",2022,["source.process.ekg-fahland-2022"],"Analyze multiple entities and dynamics through explicit event/entity graph structure instead of one case partition."),
        ("xes-event-stream-revision",2023,["source.process.ieee-xes-2023"],"Revised active interoperability standard covers event logs and streams plus extension semantics."),
        ("ocel-2-dynamic-attributes-relations",2024,["source.process.ocel-2.0"],"OCEL 2.0 adds changing object attributes and qualified event-object/object-object relations across JSON, XML and SQLite carriers."),
        ("oced-core-and-design-space",2024,["source.process.oced-core-2024"],"A community core model is separated from conventions/extensions and evaluated across independent implementations and cases."),
        ("temporal-event-knowledge-graphs",2024,["source.process.tekg-2024"],"OCEL 2.0 can be projected into a temporal EKG that preserves changing entity attributes through snapshots."),
        ("state-aware-object-centric-process-mining",2025,["source.process.sa-ocpm-2025"],"Declared state functions yield explicit state transitions and perspective-dependent state-aware events for diagnostics."),
        ("dynamic-relationship-semantics",2026,["source.process.dynamic-relations-2026"],"Formal assumptions make changing OCEL object relations manipulable without ambiguous interval meaning; evidence is still preprint-stage."),
    ]
    return [{"innovation_id":f"innovation.process.{name}","year":year,"source_refs":refs,"core_delta":delta,"ai_or_llm_dependency":False,"status":"EVIDENCE_BACKED_INNOVATION_CANDIDATE"} for name,year,refs,delta in rows]


AXIS_QUESTIONS = {
    "semantic_object":"Which events, objects, models, projections, states, alignments, measures and findings are distinct semantic subjects?",
    "semantic_role":"Which records are observations, specifications, projections, hypotheses, evidence, findings or decisions?",
    "identity_and_equality":"What identifies events, objects, projections, models, executions, states and findings, and which equivalence relation is used?",
    "grain_and_cardinality":"What are the input/output grains and multiplicities at every projection and method position?",
    "state_and_change":"Which source, object, derived, model and analysis states exist, and which transitions are observed versus generated?",
    "time":"Which event, validity, recording, processing, snapshot, model and decision times govern the result?",
    "order_and_topology":"Which total/partial orders, directly-follows relations, paths, object relations and graph scopes are asserted?",
    "partiality_and_uncertainty":"How are missing events, incomplete cuts, ambiguous mappings, censored durations and approximate results represented and propagated?",
    "authority_and_trust":"Who may define case perspectives, state models, normative models, mappings, costs and acceptance thresholds?",
    "effect_boundary":"How is pure projection/analysis separated from publication, alerting, remediation and operational mutation?",
    "representation":"Which XES, OCEL, OCED, graph, model and result carriers are used, and what semantic loss occurs at each ACL?",
    "composition_algebra":"Which projections and methods compose, under what preconditions, and how do losses/refusals propagate?",
    "compatibility_and_evolution":"What changes are carrier-, semantic-, projection-, model-, method- or evidence-compatible, and which require replay?",
    "resources_and_failure":"What finite work, memory, search, state space, deadline and cancellation bounds apply, including partial/unknown outcomes?",
    "evidence_and_conformance":"What exact source cut, method/configuration, fixtures, oracles and receipts support each bounded claim?",
    "privacy_security_safety":"What sensitive event/object/actor data and harmful inference/action paths exist, and which controls remain outside the pure method?",
}


def build() -> dict[str, Any]:
    source_rows=sources(); module_rows=modules(); law_rows=non_collapse_laws(); method_rows=methods(); expert_rows=expert_profiles(); innovation_rows=innovations()
    contributions = {row["library_id"]: row for row in load_jsonl(REGISTRY / "library-contributions.jsonl")}
    coordinate_dockets = {row["library_ref"]: row for row in load_jsonl(SEM / "library_coordinate_binding_projection/library-coordinate-binding-dockets.jsonl")}
    exact_dockets = {row["library_ref"]: row for row in load_jsonl(SEM / "p5_exact_contract_adjudication/exact-contract-dockets.jsonl")}
    subject_projections = load_jsonl(SEM / "product_coordinate_binding_projection/subject-coordinate-binding-projections.jsonl")
    products_by_library: dict[str,set[str]]={ref:set() for ref in LIBRARIES}
    subjects_by_library: dict[str,set[str]]={ref:set() for ref in LIBRARIES}
    for subject in subject_projections:
        for edge in subject["concrete_bindings"]:
            ref=edge["concrete_library_ref"]
            if ref in products_by_library:
                products_by_library[ref].add(subject["product_ref"]);subjects_by_library[ref].add(subject["subject_ref"])
    target_occurrences = {(row["axis"],row["library_ref"]):row for row in load_jsonl(SEM / "targeted_evidence_cluster_adjudication/member-adjudication-occurrences.jsonl")}

    library_rows=[]; axis_rows=[]
    module_by_id={row["module_id"]:row for row in module_rows}
    for library_ref in LIBRARIES:
        contribution=contributions[library_ref]
        refs=LIBRARY_MODULES[library_ref]
        evidence_refs=sorted({src for module in refs for src in module_by_id[module]["source_refs"]})
        library_rows.append({
            "record_kind":"process_analytics_library_semantic_binding_candidate",
            "binding_id":f"binding.process-semantic-slice.{slug(library_ref)}.v1",
            "library_ref":library_ref,
            "library_name":contribution["name"],
            "semantic_module_refs":refs,
            "evidence_refs":evidence_refs,
            "exact_contract_docket_ref":exact_dockets[library_ref]["docket_id"],
            "coordinate_binding_docket_ref":coordinate_dockets[library_ref]["binding_docket_id"],
            "downstream_subject_refs":sorted(subjects_by_library[library_ref]),
            "downstream_product_refs":sorted(products_by_library[library_ref]),
            "boundary_disposition_candidate":"RETAIN_NARROW_MODULE_BOUNDARY" if library_ref != "library.method_kernels.process_methods" else "REPLACE_FACADE_OWNERSHIP_WITH_COMPOSITION_ONLY",
            "compiler_binding":"REFUSED",
            "refusal_reasons":["OWNER_RATIFICATION_MISSING","MEMBER_AXIS_APPLICABILITY_UNRATIFIED","EXACT_CONTRACT_UNSELECTED","IMPLEMENTATIONS_UNQUALIFIED"],
            "completion_claim":False,
        })
        for axis in AXES:
            targeted=target_occurrences.get((axis,library_ref))
            axis_rows.append({
                "record_kind":"process_analytics_library_axis_decision_candidate",
                "decision_candidate_id":f"decision-candidate.process-axis.{slug(library_ref)}.{axis.replace('_','-')}.v1",
                "library_ref":library_ref,
                "axis":axis,
                "semantic_module_refs":refs,
                "coordinate_question":AXIS_QUESTIONS[axis],
                "applicability_candidate":"REQUIRED_EXPLICIT_PROFILE",
                "evidence_refs":evidence_refs,
                "targeted_member_adjudication_occurrence_ref":targeted["occurrence_id"] if targeted else None,
                "coordinate_answers":[],
                "member_applicability":"PROPOSED_OWNER_REVIEW_REQUIRED",
                "owner_decision":"UNRATIFIED",
                "status":"EVIDENCE_BACKED_DECISION_QUESTION_NOT_ANSWER",
                "canonical_gaps_closed":0,
                "completion_claim":False,
            })

    context={
        "record_kind":"bounded_context_candidate","context_id":"context.process-analytics-semantic-slice.v1","as_of":AS_OF,
        "vision":"How can observed event/object data be projected into scoped behavioral structures and analyzed without collapsing source truth, perspective, state semantics, evidence or decision authority?",
        "inside":["event-data semantic admission","object-centric event-data meaning","case/object/graph/state projections","process discovery","conformance checking","performance and bottleneck measurement","scoped finding handoff"],
        "outside":["source-system extraction and CDC","generic graph/database runtime","domain ownership of object states and thresholds","causal identification beyond declared process methods","predictive model lifecycle","operational authorization and mutation","UI and workflow"],
        "neighbors":[{"context_ref":"context.source-connectivity","relationship":"customer_supplier"},{"context_ref":"context.object-centric-event-data","relationship":"published_language"},{"context_ref":"context.analytical-finding","relationship":"open_host_service"},{"context_ref":"context.domain-decision-authority","relationship":"anti_corruption_layer"}],
        "published_language":["EventDataView","CaseProjection","ProjectionLoss","EventKnowledgeGraph","TemporalEventKnowledgeGraph","StateAwareEventView","ProcessModelCandidate","Alignment","PerformanceFinding","ProcessFindingEnvelope"],
        "ratification":"WITHHELD","completion_claim":False,
    }
    summary={"program_id":"program.process-analytics-semantic-slice.v1","as_of":AS_OF,"primary_or_official_sources":len(source_rows),"semantic_modules":len(module_rows),"non_collapse_laws":len(law_rows),"method_types":len(method_rows),"expert_learning_profiles":len(expert_rows),"recent_non_ai_innovations":len(innovation_rows),"bound_libraries":len(library_rows),"library_axis_decision_candidates":len(axis_rows),"downstream_products":len({p for values in products_by_library.values() for p in values}),"owner_decisions":0,"exact_contracts_selected":0,"qualified_implementations":0,"canonical_gaps_closed":0,"completion_claim":False}
    return {"context":context,"sources":source_rows,"modules":module_rows,"laws":law_rows,"methods":method_rows,"experts":expert_rows,"innovations":innovation_rows,"libraries":library_rows,"axes":axis_rows,"summary":summary}


def outputs() -> dict[str,str]:
    built=build(); files={
        "bounded-context.json":json.dumps(built["context"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
        "primary-sources.jsonl":"".join(canonical(row)+"\n" for row in built["sources"]),
        "semantic-modules.jsonl":"".join(canonical(row)+"\n" for row in built["modules"]),
        "non-collapse-laws.jsonl":"".join(canonical(row)+"\n" for row in built["laws"]),
        "process-method-taxonomy.jsonl":"".join(canonical(row)+"\n" for row in built["methods"]),
        "expert-learning-profiles.jsonl":"".join(canonical(row)+"\n" for row in built["experts"]),
        "innovation-records.jsonl":"".join(canonical(row)+"\n" for row in built["innovations"]),
        "library-semantic-bindings.jsonl":"".join(canonical(row)+"\n" for row in built["libraries"]),
        "library-axis-decision-candidates.jsonl":"".join(canonical(row)+"\n" for row in built["axes"]),
        "summary.json":json.dumps(built["summary"],ensure_ascii=False,sort_keys=True,indent=2)+"\n",
    }
    claims={name:{"bytes":len(text.encode()),"sha256":hashlib.sha256(text.encode()).hexdigest()} for name,text in files.items()}
    files["manifest.json"]=json.dumps({"manifest_id":"manifest.process-analytics-semantic-slice.v1","as_of":AS_OF,"files":claims,"completion_claim":False},sort_keys=True,indent=2)+"\n"
    return files


def main()->int:
    for name,text in outputs().items():(HERE/name).write_text(text)
    s=build()["summary"]
    print(f"BUILD PASS process analytics semantic slice: {s['semantic_modules']} modules, {s['method_types']} method types and {s['library_axis_decision_candidates']} exact axis questions bind {s['bound_libraries']} libraries")
    return 0


if __name__=="__main__":raise SystemExit(main())
