#!/usr/bin/env python3
"""Build the process-mining expert portfolio corpus deterministically.

The checked-in seed is intentionally explicit.  The generator adds stable IDs,
cross-record mappings, indexes, and a manifest; it does not invent citations.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EDITION = "process-mining-expert-pilot-v0.1.0"
RETRIEVED = "2026-08-25"


def source(sid, title, url, publisher, kind="paper", primary=True):
    return {
        "id": sid,
        "title": title,
        "url": url,
        "publisher_or_owner": publisher,
        "source_kind": kind,
        "is_primary_evidence": primary,
        "retrieved_on": RETRIEVED,
    }


SOURCES = [
    source("src.fahland.profile", "Dirk Fahland research profile", "https://research.tue.nl/en/persons/dirk-fahland/", "TU Eindhoven", "official_profile"),
    source("src.fahland.publications", "Dirk Fahland publication registry", "https://dblp.org/pid/67/5970.html", "DBLP", "authoritative_registry", False),
    source("src.ekg.paper", "Multi-Dimensional Event Data in Graph Databases", "https://arxiv.org/abs/2005.14552", "arXiv", "paper"),
    source("src.ekg.journal", "Multi-Dimensional Event Data in Graph Databases, journal edition", "https://doi.org/10.1007/s13740-021-00122-1", "Springer", "publisher_record"),
    source("src.ekg.handbook", "Process Mining over Multiple Behavioral Dimensions with Event Knowledge Graphs", "https://doi.org/10.1007/978-3-031-08848-3_9", "Springer", "book_chapter"),
    source("src.ekg.tutorial", "Event knowledge graph tutorials", "https://github.com/multi-dimensional-process-mining/eventgraph_tutorial", "Multi-dimensional Process Mining", "repository"),
    source("src.ekg.datasets", "Graph database event-log conversions", "https://github.com/multi-dimensional-process-mining/graphdb-eventlogs", "Multi-dimensional Process Mining", "repository"),
    source("src.ekg.zenodo", "Multi-dimensional event-data graph datasets", "https://doi.org/10.5281/zenodo.4708117", "Zenodo", "dataset"),
    source("src.schema.framework", "A Schema Framework for Graph Event Data", "https://doi.org/10.5281/zenodo.3820037", "Zenodo", "thesis"),
    source("src.task.pattern.paper", "Classifying and Detecting Task Executions and Routines in Processes Using Event Graphs", "https://doi.org/10.1007/978-3-030-85440-9_13", "Springer", "paper"),
    source("src.task.pattern.repo", "Event graph task pattern detection", "https://github.com/multi-dimensional-process-mining/event-graph-task-pattern-detection", "Multi-dimensional Process Mining", "repository"),
    source("src.task.explore", "Exploring Task Execution Patterns in Event Graphs", "https://research.tue.nl/en/publications/exploring-task-execution-patterns-in-event-graphs/", "TU Eindhoven", "paper"),
    source("src.task.aggregate", "Aggregating Event Knowledge Graphs for Task Analysis", "https://doi.org/10.1007/978-3-031-27815-0_36", "Springer", "paper"),
    source("src.missing.identifiers", "Inferring Missing Entity Identifiers from Context Using Event Knowledge Graphs", "https://doi.org/10.1007/978-3-031-41620-0_11", "Springer", "paper"),
    source("src.oced.report", "Towards a Simple and Extensible Standard for Object-Centric Event Data", "https://arxiv.org/abs/2410.14495", "arXiv", "standardization_report"),
    source("src.oced.wg", "OCED Working Group", "https://www.tf-pm.org/initiatives/oced-working-group", "IEEE Task Force on Process Mining", "working_group"),
    source("src.oced.symposium", "OCED Symposium at ICPM 2023", "https://www.tf-pm.org/resources/oced-standard/symposium-icpm-2023", "IEEE Task Force on Process Mining", "official_event_record"),
    source("src.oced.promg.docs", "PromG: OCED-PG and related publications", "https://promg-dev.github.io/promg-core/related_publications/", "PromG", "documentation"),
    source("src.oced.promg.repo", "PromG core", "https://github.com/PromG-dev/promg-core", "PromG", "repository"),
    source("src.ocel2.paper", "OCEL 2.0 Specification", "https://arxiv.org/abs/2403.01975", "arXiv", "specification"),
    source("src.ocel2.site", "OCEL 2.0 specification", "https://www.ocel-standard.org/2.0/ocel20_specification.pdf", "OCEL Standard", "specification"),
    source("src.ocel2.json", "OCEL 2.0 JSON format", "https://www.ocel-standard.org/specification/formats/json/", "OCEL Standard", "format_specification"),
    source("src.ocel2.xml", "OCEL 2.0 XML format", "https://www.ocel-standard.org/specification/formats/xml/", "OCEL Standard", "format_specification"),
    source("src.ocel2.sqlite", "OCEL 2.0 SQLite format", "https://www.ocel-standard.org/specification/formats/sqlite/", "OCEL Standard", "format_specification"),
    source("src.ocel2.datasets", "OCEL 2.0 event logs", "https://ocel-standard.org/event-logs/overview/", "OCEL Standard", "dataset_registry"),
    source("src.tekg.paper", "Transforming OCEL 2.0 to Temporal Event Knowledge Graphs", "https://arxiv.org/abs/2406.07596", "arXiv", "paper"),
    source("src.tekg.repo", "tEKG transformation implementation", "https://github.com/shahrzadkhayatbashi/BPM2024", "Khayatbashi et al.", "repository"),
    source("src.tekg.dataset", "Temporal Event Knowledge Graph datasets", "https://doi.org/10.5281/zenodo.10824628", "Zenodo", "dataset"),
    source("src.teilp.paper", "TEILP: Time Prediction over Knowledge Graphs via Logical Reasoning", "https://arxiv.org/abs/2312.15816", "arXiv", "paper"),
    source("src.process.executions", "Defining Cases and Variants for Object-Centric Event Data", "https://arxiv.org/abs/2208.03235", "arXiv", "paper"),
    source("src.hoeg.paper", "HOEG: A New Approach for Object-Centric Predictive Process Monitoring", "https://arxiv.org/abs/2404.05316", "arXiv", "paper"),
    source("src.hoeg.publisher", "HOEG publisher record", "https://doi.org/10.1007/978-3-031-61057-8_14", "Springer", "publisher_record"),
    source("src.saocpm.paper", "State-Aware Object-Centric Process Mining", "https://www.alessandroberti.it/new_papers/2025_Dina_SAOCPM.pdf", "Authors", "paper"),
    source("src.saocpm.repo", "Flowvault state-aware OCPM implementation", "https://github.com/fit-alessandro-berti/flowvault", "Alessandro Berti", "repository"),
    source("src.anomaly.paper", "Challenges of Anomaly Detection in the Object-Centric Setting", "https://arxiv.org/abs/2407.09023", "arXiv", "paper"),
    source("src.ocpm.fabric", "Object-Centric Process Mining: Unraveling the Fabric of Real Processes", "https://doi.org/10.3390/math11122691", "MDPI", "paper"),
    source("src.ocpn.discovery", "Discovering Object-Centric Petri Nets", "https://arxiv.org/abs/2010.02047", "arXiv", "paper"),
    source("src.ocpa.repo", "Object-Centric Process Analysis", "https://github.com/ocpm/ocpa", "OCPA", "repository"),
    source("src.oca.alignments", "Object-Centric Alignments", "https://arxiv.org/abs/2305.05113", "arXiv", "paper"),
    source("src.ocpi.alignments", "Object-Centric Conformance Alignments with Synchronization", "https://arxiv.org/abs/2312.08537", "arXiv", "paper"),
    source("src.performance.paper", "Unbiased, Fine-Grained Description of Processes Performance from Event Data", "https://doi.org/10.1007/978-3-319-98648-7_9", "Springer", "paper"),
    source("src.performance.repo", "Performance Spectrum Miner", "https://github.com/processmining-in-logistics/psm", "Process Mining in Logistics", "repository"),
    source("src.performance.tool", "The Performance Spectrum Miner", "https://research.tue.nl/files/125082994/BPM_2018_paper_20.pdf", "TU Eindhoven", "paper"),
    source("src.performance.batch", "Performance Mining for Batch Processing Using the Performance Spectrum", "https://research.tue.nl/en/publications/performance-mining-for-batch-processing-using-the-performance-spe/", "TU Eindhoven", "paper"),
    source("src.preprocessing", "Extracting and Pre-Processing Event Logs", "https://arxiv.org/abs/2211.04338", "arXiv", "book_chapter"),
    source("src.abstraction.paper", "Information-Preserving Abstractions of Event Data in Process Mining", "https://research.tue.nl/en/publications/information-preserving-abstractions-of-event-data-in-process-mini/", "TU Eindhoven", "paper"),
    source("src.abstraction.repo", "Information-preserving abstractions experiment", "https://github.com/dfahland/exp-abstractions-in-pm-KAIS", "Dirk Fahland", "repository"),
    source("src.scalable.paper", "Scalable Process Discovery and Conformance Checking", "https://research.tue.nl/files/101312910/Leemans2018_Article_ScalableProcessDiscoveryAndCon.pdf", "TU Eindhoven", "paper"),
    source("src.robust.thesis", "Robust Process Mining with Guarantees", "https://research.tue.nl/files/63890938/20170509_Leemans.pdf", "TU Eindhoven", "thesis"),
    source("src.precision.paper", "The Imprecisions of Precision Measures in Process Mining", "https://arxiv.org/abs/1705.03303", "arXiv", "paper"),
    source("src.artifact.lifecycle", "Artifact Lifecycle Discovery", "https://doi.org/10.1142/S021884301550001X", "World Scientific", "paper"),
    source("src.erp.artifacts", "Discovering Interacting Artifacts from ERP Systems", "https://research.tue.nl/en/publications/discovering-interacting-artifacts-from-erp-systems-extended-abstr/", "TU Eindhoven", "paper"),
    source("src.sixsigma", "Process Mining for Six Sigma", "https://research.tue.nl/en/publications/process-mining-for-six-sigma-a-guideline-and-tool-support/", "TU Eindhoven", "paper"),
    source("src.process.manifesto", "Process Mining Manifesto", "https://www.tf-pm.org/resources/process-mining-manifesto", "IEEE Task Force on Process Mining", "manifesto"),
    source("src.xes.standard", "IEEE 1849-2016 XES Standard", "https://www.xes-standard.org/", "IEEE Task Force on Process Mining", "standard"),
    source("src.prom", "ProM framework", "https://promtools.org/", "Process Mining Group", "tool"),
    source("src.pm4py", "PM4Py", "https://github.com/process-intelligence-solutions/pm4py", "Process Intelligence Solutions", "repository"),
    source("src.inductive.miner", "Discovering Block-Structured Process Models from Event Logs", "https://doi.org/10.1007/978-3-642-40176-3_19", "Springer", "paper"),
    source("src.alignment.repair", "Aligning Observed and Modeled Behavior", "https://doi.org/10.1016/j.is.2013.09.004", "Elsevier", "paper"),
    source("src.model.repair", "Repairing Process Models to Reflect Reality", "https://doi.org/10.1007/978-3-642-32885-5_16", "Springer", "paper"),
    source("src.proclets", "Discovering Synchronous Proclets", "https://doi.org/10.1007/978-3-642-15618-2_4", "Springer", "paper"),
    source("src.decomposition", "Decomposed Process Mining", "https://doi.org/10.1007/978-3-642-31095-9_24", "Springer", "paper"),
    source("src.shared.resources", "Process Mining for Systems with Shared Resources and Queues", "https://research.tue.nl/files/296758741/20230601_Denisov_hf.pdf", "TU Eindhoven", "thesis"),
    source("src.actor.performance", "Decomposing Process Performance based on Actor Behavior", "https://research.tue.nl/files/343584169/Decomposing_Process_Performance_based_on_Actor_Behavior.pdf", "TU Eindhoven", "paper"),
    source("src.dynamic_bottleneck", "Detecting system-level behavior leading to dynamic bottlenecks", "https://doi.org/10.1109/ICPM49681.2020.00014", "IEEE", "paper"),
    source("src.course", "Multi-Dimensional Process Analysis course", "https://multiprocessmining.org/learning/course-multi-dimensional-process-analysis/", "Multi Process Mining", "course"),
    source("src.process_context", "Process Mining in Context: Extending Domain Data Models for Iterative Analysis", "https://doi.org/10.1007/978-3-032-28110-4_11", "Springer", "paper"),
    source("src.filter_branch_map", "Visually Retracing and Comparing Filter Steps in Exploratory Process Mining", "https://doi.org/10.1007/978-3-032-28274-3_5", "Springer", "paper"),
    source("src.queue_object_centric", "An Object-Centric Approach to Inferring and Analyzing Queues", "https://doi.org/10.1007/978-3-032-13426-4_35", "Springer", "paper"),
    source("src.oced_pg_dataset", "Event Data and Semantic Header for OCED-PG", "https://doi.org/10.5281/zenodo.8296559", "Zenodo", "dataset"),
    source("src.object_centric_case_2026", "What is an Object-Centric Case? An Exploration", "https://research.tue.nl/en/publications/what-is-anobject-centric-case-an-exploration/", "TU Eindhoven", "book_chapter"),
]


EXPERTS = [
    ("expert.dirk_fahland", "Dirk Fahland", "0000-0002-1993-9363", ["event knowledge graphs", "multi-dimensional process mining", "OCED", "task and performance analysis", "formal process models"]),
    ("expert.wil_van_der_aalst", "Wil M. P. van der Aalst", "0000-0002-0955-6940", ["process mining foundations", "OCEL", "object-centric process mining", "Petri nets"]),
    ("expert.alessandro_berti", "Alessandro Berti", "0000-0002-3279-4795", ["OCEL", "PM4Py", "object-centric discovery", "state-aware OCPM"]),
    ("expert.sander_leemans", "Sander J. J. Leemans", None, ["inductive mining", "scalability", "guarantees", "abstractions"]),
    ("expert.stefan_esser", "Stefan Esser", None, ["event knowledge graphs", "property-graph event data"]),
    ("expert.eva_klijn", "Eva L. Klijn", None, ["task execution patterns", "event-graph aggregation", "performance mining"]),
    ("expert.felix_mannhardt", "Felix Mannhardt", "0000-0003-1733-777X", ["task analysis", "process mining"]),
    ("expert.vadim_denisov", "Vadim Denisov", None, ["performance spectrum", "shared resources", "queue inference"]),
    ("expert.marco_montali", "Marco Montali", None, ["object-centric semantics", "conformance", "formal models"]),
    ("expert.gyunam_park", "Gyunam Park", None, ["object-centric performance and monitoring"]),
    ("expert.jan_niklas_adams", "Jan Niklas Adams", None, ["OCEL", "object-centric directly-follows graphs"]),
    ("expert.shahrzad_khayatbashi", "Shahrzad Khayatbashi", "0000-0001-7621-0985", ["temporal event knowledge graphs"]),
    ("expert.tim_smit", "Tim K. Smit", None, ["HOEG", "object-centric predictive monitoring"]),
    ("expert.hajo_reijers", "Hajo A. Reijers", None, ["process science", "predictive monitoring"]),
    ("expert.xixi_lu", "Xixi Lu", None, ["process mining", "object-centric prediction"]),
    ("expert.dina_kretzschmann", "Dina Kretzschmann", "0009-0002-4413-4345", ["state-aware object-centric process mining"]),
    ("expert.ava_swevels", "Ava Swevels", None, ["OCED-PG", "semantic headers", "missing identifier inference"]),
    ("expert.olaf_hartig", "Olaf Hartig", None, ["temporal event knowledge graphs", "graph data"]),
    ("expert.amin_jalali", "Amin Jalali", "0000-0002-6633-8587", ["temporal event knowledge graphs", "process mining"]),
    ("expert.zahra_toosinezhad", "Zahra Toosinezhad", None, ["dynamic bottleneck detection", "system-level event patterns"]),
    ("expert.ozge_koroglu", "Özge Köroğlu", None, ["material-handling systems", "dynamic bottlenecks"]),
    ("expert.elena_belkina", "Elena Belkina", None, ["Performance Spectrum Miner", "performance visualization"]),
    ("expert.francesca_zerbato", "Francesca Zerbato", None, ["domain-context process mining", "exploratory-analysis provenance"]),
    ("expert.laura_didden", "Laura Didden", None, ["filter provenance", "exploratory process mining"]),
    ("expert.sander_van_gansewinkel", "Sander van Gansewinkel", None, ["object-centric queue inference", "queue performance"]),
]


def c(cid, name, kind, date, authors, sources, context, problem, objects, operators,
      algorithms, guarantees, assumptions, limitations, categories, status="core_candidate",
      related=(), decisions=()):
    """A contribution, not merely a publication row."""
    return {
        "id": cid,
        "name": name,
        "artifact_kind": kind,
        "status": status,
        "version_or_date": date,
        "authors_or_maintainers": authors,
        "expert_roles": [{"expert_id": expert, "role": "author"} for expert in authors],
        "attribution_scope": "Portfolio-linked authors are encoded here; the cited primary source remains authoritative for the complete byline and role order.",
        "primary_source_ids": list(sources),
        "bounded_context": context,
        "problem_or_question": problem,
        "formal_objects_or_types": list(objects),
        "data_or_event_graph_model": f"{context}: " + "; ".join(objects),
        "operators": list(operators),
        "algorithms": list(algorithms),
        "guarantees": list(guarantees),
        "assumptions": list(assumptions),
        "uncertainty_or_partiality": ["absence of evidence is not conformance", "results are conditional on event-data semantics and completeness"],
        "lifecycle": ["declare semantics", "validate input", "execute", "emit result and evidence", "invalidate on semantic or version change"],
        "inputs": [objects[0] if objects else "typed domain input"],
        "outputs": [name],
        "runtime_resource_posture": ["resource bounds are implementation- and dataset-dependent unless benchmarked", "preserve deterministic configuration and edition identity"],
        "evidence_or_benchmarks": [f"primary evidence: {sid}" for sid in sources],
        "limitations_or_counterevidence": list(limitations),
        "related_or_superseded_artifact_ids": list(related),
        "categories": list(categories),
        "exposed_decisions": list(decisions) or ["input representation", "semantic projection", "operator parameters", "failure policy", "evidence retention"],
    }


DIRK = "expert.dirk_fahland"
WIL = "expert.wil_van_der_aalst"
BERTI = "expert.alessandro_berti"
LEEMANS = "expert.sander_leemans"


CONTRIBUTIONS = [
    c("art.ekg.model", "Event Knowledge Graph core model", "formal_model", "2020-05-29", ["expert.stefan_esser", DIRK], ["src.ekg.paper", "src.ekg.journal"], "event_data_representation", "Represent multi-entity event data without flattening to one case notion.", ["labeled property graph", "event", "entity", "class", "correlation edge", "directly-follows edge"], ["correlate", "derive directly-follows", "traverse", "aggregate"], ["record-to-graph conversion", "entity-scoped directly-follows derivation"], ["explicit structural and temporal relations"], ["timestamps and entity correlations are meaningful"], ["base EKG does not intrinsically retain every attribute-history semantics"], ["object-centric semantics", "event-data exchange", "behavioral representation"]),
    c("art.ekg.schema_framework", "PG-schema framework for graph event data", "schema", "2020-02-19", ["expert.stefan_esser", DIRK], ["src.schema.framework", "src.oced.promg.docs"], "event_data_representation", "Constrain event graph structure and specialize it for a domain.", ["PG-schema", "base schema", "specialized schema", "node type", "edge type"], ["inherit", "specialize", "validate"], ["schema validation"], ["schema-level type constraints"], ["property-graph implementation supports required schema features"], ["schema does not alone establish domain truth"], ["schema", "ontology", "event-data exchange"]),
    c("art.ekg.raw_to_graph", "Raw-record to EKG transformation", "transformation", "2020", ["expert.stefan_esser", DIRK], ["src.ekg.paper", "src.ekg.datasets"], "event_data_preparation", "Convert relational or CSV records into explicit event/entity graphs.", ["raw record", "event node", "entity node", "correlation", "ordering relation"], ["identify", "materialize", "link", "order"], ["parameterized Cypher transformation"], ["repeatable transformation for declared mappings"], ["stable identifiers and parseable timestamps"], ["bad source semantics propagate into the graph"], ["extraction", "transformation", "event knowledge graph"]),
    c("art.ekg.df_semantics", "Entity-qualified directly-follows semantics", "relation_semantics", "2020", ["expert.stefan_esser", DIRK], ["src.ekg.paper", "src.ekg.handbook"], "behavioral_relation", "Avoid an unqualified directly-follows relation that conflates object perspectives.", ["event pair", "shared entity", "entity type", "time order", "intermediate event"], ["derive", "qualify", "filter"], ["entity-scoped adjacency query"], ["directly-follows is relative to an entity or projection"], ["a deterministic event ordering policy exists"], ["ties and uncertain order require explicit policy"], ["behavioral semantics", "query operator"]),
    c("art.ekg.multi_entity_dfg", "Multi-entity directly-follows aggregation", "query_operator", "2022", [DIRK], ["src.ekg.handbook", "src.ekg.tutorial"], "process_discovery", "Summarize behavior across interacting entity types without flattening.", ["event class", "entity-qualified directly-follows", "aggregate edge", "frequency"], ["classify", "group", "count", "project"], ["Cypher aggregation queries"], ["aggregation is traceable to event relations"], ["classification functions are declared"], ["frequency summary is not a behavioral model with execution semantics"], ["process discovery", "aggregation"]),
    c("art.ekg.proclet_discovery", "Proclet discovery from EKG", "algorithm", "2022", [DIRK], ["src.ekg.handbook", "src.ekg.tutorial", "src.proclets"], "process_discovery", "Discover interacting object lifecycles and synchronizations.", ["entity-local activity", "local flow", "synchronization edge", "proclet"], ["classify", "aggregate local flow", "link synchronizations"], ["proclet discovery queries"], ["separates local lifecycle from interaction"], ["events are correctly correlated to entities"], ["discovered proclets inherit incompleteness and noise"], ["process discovery", "behavioral model", "synchronization"]),
    c("art.ekg.graph_datasets", "Five converted multi-dimensional event datasets", "dataset", "2021", ["expert.stefan_esser", DIRK], ["src.ekg.datasets", "src.ekg.zenodo"], "benchmark_data", "Make graph event-data research reproducible.", ["converted event graph", "source event log", "Cypher import script"], ["download", "restore", "query"], ["scripted conversion"], ["versioned research artifacts"], ["source logs remain obtainable"], ["limited domain diversity and database-version sensitivity"], ["dataset", "benchmark", "reproducibility"]),
    c("art.ekg.tutorial_suite", "Event knowledge graph tutorial suite", "tutorial", "2022", [DIRK, "expert.stefan_esser"], ["src.ekg.tutorial", "src.course"], "practice_enablement", "Teach construction, querying, discovery, and object-centric analysis as separable steps.", ["tutorial dataset", "Cypher query", "Neo4j instance", "expected graph"], ["import", "construct", "query", "aggregate"], ["executable tutorial sequence"], ["examples expose transformations"], ["Neo4j/Cypher environment"], ["tutorial success is not production qualification"], ["tooling", "education", "library boundary"]),
    c("art.task.execution_taxonomy", "Task-execution pattern taxonomy", "taxonomy", "2021", ["expert.eva_klijn", "expert.felix_mannhardt", DIRK], ["src.task.pattern.paper", "src.task.explore"], "task_behavior_analysis", "Describe how actors organize work across cases rather than only within a case.", ["task event", "actor", "case/entity", "execution pattern", "routine"], ["classify", "detect", "compare"], ["event-graph pattern matching"], ["patterns are explicitly defined over graph relations"], ["resource identity and temporal ordering are available"], ["pattern meaning remains domain-dependent"], ["task analysis", "organizational mining", "diagnostics"]),
    c("art.task.pattern_detector", "Task-execution pattern detector", "tool", "2021", ["expert.eva_klijn", "expert.felix_mannhardt", DIRK], ["src.task.pattern.repo", "src.task.pattern.paper"], "task_behavior_analysis", "Execute reusable task-pattern queries on event knowledge graphs.", ["EKG", "pattern specification", "match", "evidence subgraph"], ["configure", "detect", "return matches"], ["Cypher-based pattern detection"], ["matches can retain graph witnesses"], ["input conforms to expected EKG schema"], ["tool availability and schema compatibility require qualification"], ["tool", "runtime library", "diagnostics"]),
    c("art.task.aggregation_operators", "Task-aware EKG aggregation operators", "query_operator", "2023", ["expert.eva_klijn", "expert.felix_mannhardt", DIRK], ["src.task.aggregate"], "task_behavior_analysis", "Aggregate graph event data without erasing actor/task structures required for analysis.", ["task execution", "actor", "event class", "aggregate graph"], ["group", "collapse", "retain relation", "compare"], ["labeled-property-graph query operators"], ["operator semantics are explicit"], ["task executions have already been identified"], ["aggregation can still lose information; residual must be recorded"], ["aggregation", "task analysis", "information loss"]),
    c("art.task.actor_work_division", "Actor work-division analysis", "analytical_method", "2023", ["expert.eva_klijn", "expert.felix_mannhardt", DIRK], ["src.task.aggregate", "src.actor.performance"], "organizational_diagnostics", "Compare work division and execution patterns between actors.", ["actor", "task execution", "handover", "workload", "performance observation"], ["segment", "compare", "decompose"], ["graph aggregation plus descriptive comparison"], ["reported differences trace to event evidence"], ["actor identifiers are valid and ethically usable"], ["association is not causation; workforce interpretation can harm people"], ["diagnostics", "human process", "performance"]),
    c("art.missing_id.context_graph", "Context graph for missing identifiers", "formal_model", "2023", ["expert.ava_swevels", DIRK], ["src.missing.identifiers"], "event_data_quality", "Represent contextual evidence from which absent entity identifiers might be inferred.", ["event", "known entity", "candidate entity", "context path", "identifier hypothesis"], ["construct context", "score candidate", "attach hypothesis"], ["graph-context inference"], ["inference can be accompanied by evidence"], ["context correlates with true identity"], ["inferred identity is not observed identity"], ["data quality", "identity inference", "evidence"]),
    c("art.missing_id.inference", "Missing entity-identifier inference", "algorithm", "2023", ["expert.ava_swevels", DIRK], ["src.missing.identifiers", "src.oced.promg.docs"], "event_data_quality", "Recover candidate correlations while distinguishing inference from source fact.", ["context graph", "candidate assignment", "confidence", "provenance"], ["infer", "rank", "accept", "refuse"], ["context-based entity identification"], ["accepted assignments remain marked as inferred"], ["candidate-generating context is adequate"], ["false correlations can create false process behavior"], ["data repair", "entity resolution", "partiality"]),
    c("art.oced.core_metamodel", "OCED core meta-model", "standard_model", "2024-10-18", [DIRK, "expert.marco_montali", WIL], ["src.oced.report", "src.oced.wg"], "event_data_standardization", "Define a small common model underlying known object-centric event-data use cases.", ["event", "event type", "object", "object type", "attribute", "time", "event-object relation", "object-object relation"], ["type", "relate", "qualify", "extend"], ["metamodel conformance"], ["core distinguishes common semantics from conventions and extensions"], ["domain meaning is supplied outside the core"], ["core intentionally does not solve every use case"], ["OCED", "standard", "semantic model"]),
    c("art.oced.design_space", "OCED design-space and trade-off catalog", "design_space", "2024-10-18", [DIRK, "expert.marco_montali", WIL], ["src.oced.report"], "event_data_standardization", "Make representation choices and their incompatibilities explicit.", ["core construct", "usage pattern", "convention", "extension", "trade-off"], ["compare", "select", "extend", "refuse"], ["design-space analysis"], ["limitations are first-class rather than hidden"], ["use cases sampled are representative"], ["not an IEEE standard edition; community proposal status matters"], ["decision catalog", "standardization", "compatibility"]),
    c("art.oced.reference_implementations", "Five OCED reference implementations", "implementation_evidence", "2024", [DIRK, "expert.marco_montali", WIL], ["src.oced.report", "src.oced.symposium"], "event_data_standardization", "Falsify the claim that the OCED core cannot be implemented independently.", ["core model", "implementation", "case study", "exchange artifact"], ["implement", "compare", "report lesson"], ["independent implementation comparison"], ["multiple implementations support feasibility, not semantic completeness"], ["implementations genuinely independent"], ["case studies do not prove universal coverage"], ["conformance", "reference implementation", "standardization"]),
    c("art.oced.semantic_header", "OCED semantic header", "mapping_contract", "2023", [DIRK, "expert.ava_swevels"], ["src.oced.symposium", "src.oced.promg.docs"], "event_data_preparation", "Declare how legacy records map to OCED concepts and domain reference ontology.", ["dataset description", "raw record type", "semantic concept", "mapping rule", "reference ontology"], ["declare source field", "construct semantic node", "construct relation", "validate"], ["rule-to-query compilation"], ["mapping is inspectable and repeatable"], ["legacy fields have stable meanings"], ["declaration can be wrong; validation against domain evidence remains necessary"], ["semantic mapping", "data contract", "compiler front-end"]),
    c("art.oced.pg_base_ontology", "OCED-PG base ontology", "ontology", "2023", [DIRK, "expert.ava_swevels"], ["src.oced.promg.docs", "src.oced.promg.repo"], "event_data_representation", "Formalize OCED plus a raw-record layer as a property-graph schema.", ["semantic layer", "record layer", "base ontology", "PG-schema"], ["specialize", "validate", "transform"], ["schema inheritance"], ["base and domain-specific meanings remain separated"], ["PG-schema semantics are supported"], ["property-graph realization is not the OCED abstract model itself"], ["ontology", "representation", "schema"]),
    c("art.oced.pg_reference_ontology", "OCED-PG domain reference ontology", "ontology", "2023", [DIRK, "expert.ava_swevels"], ["src.oced.promg.docs", "src.oced.promg.repo"], "domain_semantics", "Specialize the OCED base ontology with domain event, object, relation, and record meanings.", ["domain event type", "domain object type", "domain relation", "legacy record binding"], ["inherit", "specialize", "bind", "validate"], ["ontology specialization"], ["domain names do not alter base OCED identity"], ["domain ontology is governed"], ["domain ontology coverage is contextual, not universal"], ["domain ontology", "published language", "bounded context"]),
    c("art.oced.pg_elt", "OCED-PG declarative ELT", "tool", "2023", [DIRK, "expert.ava_swevels"], ["src.oced.promg.docs", "src.oced.promg.repo"], "event_data_preparation", "Compile semantic-header rules into executable graph transformations.", ["raw record graph", "semantic header", "transformation rule", "OCED graph"], ["load", "compile", "transform", "export"], ["mapping-rule to Cypher generation"], ["declarative mapping and execution artifact can be traced"], ["Neo4j runtime and source access"], ["runtime behavior and scalability require target qualification"], ["ELT", "compiler", "runtime adapter"]),
    c("art.ocel2.metamodel", "OCEL 2.0 conceptual model", "standard_model", "2024-03-04", [BERTI, "expert.jan_niklas_adams", WIL], ["src.ocel2.paper", "src.ocel2.site"], "event_log_exchange", "Exchange object-centric logs with typed events, objects, relations, and changing attributes.", ["event type", "object type", "event", "object", "attribute change", "qualified relation"], ["serialize", "parse", "validate"], ["format validation"], ["three official serializations represent the specified model"], ["producer assigns intended semantics"], ["format validity does not establish event-data quality or domain truth"], ["OCEL", "exchange", "standard"]),
    c("art.ocel2.json", "OCEL 2.0 JSON serialization", "exchange_format", "2.0", [BERTI, "expert.jan_niklas_adams", WIL], ["src.ocel2.json", "src.ocel2.site"], "event_log_exchange", "Serialize OCEL 2.0 as a document format.", ["JSON object", "objectTypes", "eventTypes", "objects", "events"], ["encode", "decode", "schema-validate"], ["JSON serialization"], ["references and field types can be validated"], ["whole log is representable as a JSON document"], ["large logs may exceed practical memory envelopes"], ["serialization", "adapter", "OCEL"]),
    c("art.ocel2.xml", "OCEL 2.0 XML serialization", "exchange_format", "2.0", [BERTI, "expert.jan_niklas_adams", WIL], ["src.ocel2.xml", "src.ocel2.site"], "event_log_exchange", "Serialize OCEL 2.0 with XML tooling.", ["XML element", "typed attribute", "reference"], ["encode", "decode", "validate"], ["XML serialization"], ["schema-valid documents preserve declared fields"], ["XML processing policy is explicit"], ["XML parser security and scale are adapter concerns"], ["serialization", "adapter", "OCEL"]),
    c("art.ocel2.sqlite", "OCEL 2.0 SQLite serialization", "exchange_format", "2.0", [BERTI, "expert.jan_niklas_adams", WIL], ["src.ocel2.sqlite", "src.ocel2.site"], "event_log_exchange", "Store and exchange OCEL 2.0 relationally.", ["SQLite database", "type table", "event table", "object table", "relation table"], ["insert", "query", "validate foreign key"], ["relational encoding"], ["relational constraints can be checked"], ["SQLite edition and schema match"], ["physical schema is not the abstract OCEL model"], ["serialization", "persistence adapter", "OCEL"]),
    c("art.ocel2.dataset_registry", "OCEL 2.0 dataset registry", "dataset_registry", "2023-present", ["expert.jan_niklas_adams", BERTI, WIL], ["src.ocel2.datasets"], "benchmark_data", "Provide citable object-centric logs for reproducibility and interoperability tests.", ["dataset record", "DOI", "domain description", "serialization"], ["register", "download", "cite"], ["dataset publication"], ["dataset identities and citations are explicit"], ["external repositories remain available"], ["synthetic examples do not establish industrial generality"], ["dataset", "benchmark", "conformance test"]),
    c("art.tekg.model", "Temporal Event Knowledge Graph", "formal_model", "2024-06-11", ["expert.shahrzad_khayatbashi", "expert.olaf_hartig", "expert.amin_jalali"], ["src.tekg.paper"], "temporal_event_data", "Represent object attribute evolution explicitly in an EKG.", ["entity", "snapshot", "event", "class", "time", "snapshot succession"], ["snapshot", "order", "correlate", "derive directly-follows"], ["OCEL-to-tEKG transformation"], ["attribute histories are materialized as ordered snapshots"], ["OCEL timestamps provide sufficient change order"], ["relationship temporality and simultaneous changes need explicit semantics"], ["temporal graph", "object-centric semantics", "representation"]),
    c("art.tekg.transform", "OCEL 2.0 to tEKG transformation", "algorithm", "2024", ["expert.shahrzad_khayatbashi", "expert.olaf_hartig", "expert.amin_jalali"], ["src.tekg.paper", "src.tekg.repo"], "event_data_transformation", "Convert official OCEL 2.0 logs into temporal event knowledge graphs.", ["OCEL event", "OCEL object", "attribute change", "tEKG snapshot", "df edge"], ["create", "map", "snapshot", "derive", "prune"], ["batch mode", "live mode", "hybrid mode", "directly-follows construction"], ["specified output graph for declared transformation"], ["OCEL input conforms to edition 2.0"], ["different modes have different runtime/resource behavior"], ["transformation", "adapter", "temporal graph"]),
    c("art.tekg.dataset", "Transformed tEKG benchmark dumps", "dataset", "2024-03-16", ["expert.shahrzad_khayatbashi", "expert.olaf_hartig", "expert.amin_jalali"], ["src.tekg.dataset", "src.tekg.repo"], "benchmark_data", "Provide concrete database dumps for transformation evaluation.", ["OCEL source", "Neo4j dump", "database version", "checksum"], ["restore", "query", "compare"], ["batch transformation"], ["artifact checksums and source lineage are published"], ["Neo4j 5.12 compatibility"], ["2.1GB corpus is narrow and target-specific"], ["dataset", "benchmark", "runtime qualification"]),
    c("art.process_execution.model", "Object-centric process execution", "formal_model", "2022-08-05", ["expert.jan_niklas_adams", WIL], ["src.process.executions"], "case_construction", "Define a case-like unit over graph-structured OCED without destructive flattening.", ["event-object graph", "process execution", "extraction boundary", "leading object"], ["extract", "connect", "restrict"], ["graph-based execution extraction"], ["execution definition is explicit and repeatable"], ["selection parameters define meaningful boundaries"], ["there is no universally correct object-centric case"], ["case construction", "graph projection", "partiality"]),
    c("art.process_variant.model", "Object-centric behavioral variant", "formal_model", "2022-08-05", ["expert.jan_niklas_adams", WIL], ["src.process.executions"], "variant_analysis", "Compare object-centric executions by behavior rather than linear trace equality.", ["process execution graph", "event label", "graph isomorphism", "variant class"], ["canonicalize", "test isomorphism", "group"], ["attribute-respecting graph isomorphism"], ["variant equality is defined relative to selected attributes"], ["graphs are finite and chosen labels are stable"], ["isomorphism cost and attribute selection affect scalability and meaning"], ["variant analysis", "graph algorithm", "canonicalization"]),
    c("art.hoeg.encoding", "Heterogeneous Object Event Graph encoding", "representation", "2024-04-08", ["expert.tim_smit", "expert.hajo_reijers", "expert.xixi_lu"], ["src.hoeg.paper", "src.hoeg.publisher"], "predictive_monitoring", "Encode events and heterogeneous objects without aggregating object features.", ["heterogeneous graph", "event node", "object node", "typed edge", "feature vector"], ["encode prefix", "retain object feature", "batch graphs"], ["HOEG encoding"], ["object features remain associated with typed nodes"], ["OCEL contains predictive attributes"], ["not authored by Fahland; prediction benchmark does not make it an exchange standard"], ["predictive encoding", "graph representation"], "reference_only_noncore"),
    c("art.hoeg.predictor", "HOEG heterogeneous-GNN remaining-time predictor", "predictive_model", "2024", ["expert.tim_smit", "expert.hajo_reijers", "expert.xixi_lu"], ["src.hoeg.paper", "src.hoeg.publisher"], "predictive_monitoring", "Predict remaining time from object-centric execution prefixes.", ["HOEG", "heterogeneous GNN", "remaining-time target", "trained parameters"], ["train", "predict", "evaluate"], ["heterogeneous graph neural network"], ["empirical benchmark only"], ["training/test distributions are sufficiently related"], ["excluded from the non-AI core; performance depends on informative attributes"], ["prediction", "machine learning", "benchmark"], "excluded_ai_method"),
    c("art.saocpm.state_semantics", "State-Aware OCEL formal model", "formal_model", "2025", ["expert.dina_kretzschmann", BERTI, WIL], ["src.saocpm.paper"], "state_aware_ocpm", "Make object state and state changes explicit in object-centric process analysis.", ["base OCEL", "always-defined string-valued object-state attribute", "extended event set E'", "generated state-change event E''", "state-aware relabeled event", "total event order with tie-break"], ["derive state", "emit transition at t-epsilon", "preserve original event identity", "refine activity label", "tie-break"], ["State-Aware OCEL construction", "Coalesced State-Aware OCEL construction"], ["state-change events expose old/new state and remain linked to the affected object", "original event identity is preserved during state-aware relabeling"], ["one chosen state attribute is defined for every object at every time and has string values", "state derivation rule is domain-valid"], ["t-epsilon is a modeling convention and simultaneous-event ordering requires a policy", "activity relabeling can multiply classes and obscure the original activity dimension unless retained separately"], ["state machine", "object-centric semantics", "event enrichment"]),
    c("art.saocpm.discovery", "State-aware object-centric process discovery", "analytical_method", "2025", ["expert.dina_kretzschmann", BERTI, WIL], ["src.saocpm.paper", "src.saocpm.repo"], "process_discovery", "Discover behavior conditioned on object state.", ["state-aware OCEL", "state-refined activity", "object-centric model"], ["enrich", "discover", "visualize"], ["SA-OCPM pipeline"], ["output distinguishes state transitions from activities"], ["state mapping is supplied"], ["state proliferation can reduce comprehensibility"], ["process discovery", "state awareness", "tooling"]),
    c("art.oc_anomaly.taxonomy", "Object-centric anomaly dimensions", "taxonomy", "2024-07-12", [BERTI, WIL, DIRK], ["src.anomaly.paper"], "process_diagnostics", "Separate lifecycle anomalies from interaction anomalies and state the role of domain knowledge.", ["object lifecycle", "object interaction", "anomaly dimension", "domain constraint"], ["enumerate", "feature-propagate", "detect", "explain"], ["dimensionality reduction and anomaly detection candidates"], ["dimensions are explicit; detections remain hypotheses"], ["domain context determines relevance"], ["anomaly score is not proof of defect or root cause"], ["anomaly detection", "diagnostics", "domain knowledge"]),
    c("art.oc_anomaly.feature_propagation", "Object-centric feature propagation", "operation", "2024", [BERTI, WIL, DIRK], ["src.anomaly.paper"], "process_diagnostics", "Propagate contextual features over event-object relations for anomaly analysis.", ["event feature", "object feature", "relation", "propagated feature"], ["aggregate", "propagate", "normalize"], ["graph feature propagation"], ["operation can be replayed from declared graph and parameters"], ["propagation neighborhood is meaningful"], ["leakage and over-smoothing can create misleading anomalies"], ["feature engineering", "graph operation", "diagnostics"]),
    c("art.ocpm.fabric_principles", "Object-centric process-fabric principles", "conceptual_framework", "2023-06-13", [WIL], ["src.ocpm.fabric"], "object_centric_process_mining", "Explain why multi-object operational reality cannot safely be reduced to isolated traces.", ["event", "object", "object relation", "process fabric", "view"], ["lift", "project", "analyze"], ["object-centric lifting patterns"], ["view construction starts from one object-centric source"], ["OCED semantics are controlled"], ["tutorial framework is not one executable algorithm"], ["process mining", "object-centricity", "method family"]),
    c("art.ocpn.formalism", "Object-Centric Petri Net", "formal_model", "2020-10-05", [WIL, BERTI], ["src.ocpn.discovery", "src.ocpm.fabric"], "behavioral_model", "Model transitions consuming and producing collections of typed objects.", ["place", "transition", "object type", "variable arc", "typed token"], ["enable", "fire", "project"], ["object-centric Petri-net semantics"], ["formal firing semantics"], ["object types and correlations are meaningful"], ["some interactions and identities are abstracted"], ["behavioral model", "Petri net", "object-centric semantics"]),
    c("art.ocpn.discovery", "Object-Centric Petri Net discovery", "algorithm", "2020", [WIL, BERTI], ["src.ocpn.discovery", "src.ocpa.repo"], "process_discovery", "Discover an OCPN from object-centric event data.", ["OCEL", "flattened object-type projections", "Petri net fragments", "OCPN"], ["project", "discover", "merge"], ["per-object-type discovery and composition"], ["discovered net has defined OCPN structure"], ["projected behavior is sufficiently representative"], ["flattening within projections can introduce convergence/divergence effects"], ["process discovery", "algorithm", "object-centric model"]),
    c("art.oca.alignment", "Object-centric alignment", "conformance_method", "2023-05-08", ["expert.wil_van_der_aalst"], ["src.oca.alignments"], "conformance_checking", "Relate object-centric observed behavior to an OCPN with explainable deviations.", ["OCEL execution", "OCPN run", "synchronous move", "log move", "model move", "cost"], ["align", "minimize cost", "diagnose"], ["object-centric alignment search"], ["optimality relative to cost function and search completeness"], ["cost model and bounded execution are declared"], ["alignment depends critically on execution construction and cost choices"], ["conformance", "diagnostics", "optimization"]),
    c("art.ocpi.formalism", "Object-centric Petri nets with identifiers", "formal_model", "2023-12-13", ["expert.marco_montali"], ["src.ocpi.alignments"], "behavioral_model", "Track object identity and synchronization dependencies during conformance.", ["typed identifier", "token", "transition", "synchronization", "binding"], ["bind", "synchronize", "fire"], ["identifier-aware firing semantics"], ["formal identity-preserving execution semantics"], ["identifiers are stable"], ["state-space and SMT cost may be high"], ["behavioral model", "identity", "synchronization"]),
    c("art.ocpi.smt_alignment", "SMT object-centric conformance encoding", "algorithm", "2023", ["expert.marco_montali"], ["src.ocpi.alignments"], "conformance_checking", "Compute alignments that respect identity and synchronization.", ["OPID", "event data", "SMT variables", "cost objective", "alignment"], ["encode", "solve", "decode"], ["SMT optimization"], ["solver result is optimal if solver proves optimum under encoding"], ["bounded encoding faithfully represents task"], ["solver unknown/timeouts are legitimate partial outcomes"], ["conformance", "solver", "kernel qualification"]),
    c("art.performance.spectrum", "Performance spectrum", "analytical_representation", "2018", ["expert.vadim_denisov", DIRK, WIL], ["src.performance.paper", "src.performance.tool"], "performance_analysis", "Reveal fine-grained, non-steady performance without prematurely aggregating cases.", ["process step", "segment", "start time", "end time", "case flow", "spectrum"], ["classify", "bin", "filter", "visualize"], ["segment construction and visual aggregation"], ["individual flows remain inspectable in the representation"], ["event timestamps and step classifier are valid"], ["visual patterns require careful interpretation and do not prove causes"], ["performance", "visual analytics", "bottleneck diagnosis"]),
    c("art.performance.patterns", "Performance-spectrum pattern catalog", "taxonomy", "2018", ["expert.vadim_denisov", DIRK, WIL], ["src.performance.paper", "src.performance.repo"], "performance_diagnostics", "Identify queueing, batching, prioritization, overtaking, and slow-mover signatures.", ["segment geometry", "time window", "flow cluster", "pattern hypothesis"], ["detect", "classify", "compare"], ["visual/pattern analysis"], ["pattern observations retain supporting segments"], ["sampling and display preserve relevant structure"], ["signature is diagnostic evidence, not a unique causal explanation"], ["diagnostics", "queueing", "batching", "bottleneck"]),
    c("art.performance.miner", "Performance Spectrum Miner", "tool", "2018", ["expert.vadim_denisov", "expert.elena_belkina", DIRK], ["src.performance.repo", "src.performance.tool"], "performance_analysis", "Operationalize spectrum generation, exploration, filtering, classification, and export.", ["XES/CSV log", "session file", "segment", "bin", "classifier"], ["transform", "filter", "zoom", "aggregate", "export"], ["disk-backed spectrum transformation"], ["standalone and ProM implementations are published"], ["input fits supported event schema"], ["interactive visual output is not a machine proof of bottleneck"], ["tool", "runtime library", "visual analytics"]),
    c("art.performance.batch", "Batch-processing performance mining", "analytical_method", "2019", ["expert.eva_klijn", DIRK], ["src.performance.batch", "src.performance.repo"], "performance_diagnostics", "Detect and characterize batching behavior in process performance.", ["batch", "segment", "cohort", "waiting time", "processing time"], ["group co-moving cases", "compare batches", "attribute delay"], ["performance-spectrum batch analysis"], ["batch observations are grounded in event-time patterns"], ["timestamps expose batching boundaries"], ["batch signature may have multiple operational explanations"], ["batching", "performance", "root-cause hypothesis"]),
    c("art.dynamic_bottleneck.system_event", "System-level event abstraction", "formal_model", "2020-10", ["expert.zahra_toosinezhad", DIRK, "expert.ozge_koroglu", WIL], ["src.dynamic_bottleneck"], "performance_diagnostics", "Represent temporal patterns spanning cases in one process step as system-level events.", ["case event", "process step", "temporal cross-case pattern", "system-level event", "location"], ["aggregate cross-case pattern", "timestamp", "locate"], ["temporal event-pattern aggregation"], ["system-level event retains the supporting low-level event pattern"], ["events share a meaningful process-step and time basis"], ["aggregation boundary can create or hide apparent system behavior"], ["dynamic bottleneck", "event aggregation", "diagnostics"]),
    c("art.dynamic_bottleneck.cascade", "Spatio-temporal system-event cascade", "formal_model", "2020-10", ["expert.zahra_toosinezhad", DIRK, "expert.ozge_koroglu", WIL], ["src.dynamic_bottleneck"], "performance_diagnostics", "Correlate system-level events into propagating behavior leading to a dynamic bottleneck.", ["system-level event", "spatial condition", "temporal condition", "cascade", "dynamic bottleneck"], ["correlate", "chain", "bound in time", "bound in location"], ["spatio-temporal cascade construction"], ["each cascade edge satisfies declared spatial and temporal conditions"], ["layout and time thresholds are valid"], ["correlation alone does not prove causation outside the evaluated physical-system setting"], ["dynamic bottleneck", "event correlation", "causal hypothesis"]),
    c("art.dynamic_bottleneck.predecessor_patterns", "Frequent pre-bottleneck cascade patterns", "analytical_method", "2020-10", ["expert.zahra_toosinezhad", DIRK, "expert.ozge_koroglu", WIL], ["src.dynamic_bottleneck"], "root_cause_diagnostics", "Discover recurring classes of system behavior that precede rare dynamic bottlenecks.", ["cascade", "pattern class", "frequency", "bottleneck onset", "physical-layout evidence"], ["classify cascade", "mine frequent pattern", "verify explanation"], ["frequent cascade-pattern discovery"], ["airport case-study detections were checked against physical layout and processing"], ["the evaluated material-handling system exposes relevant events and topology"], ["external validity beyond the evaluated airport/system requires independent qualification"], ["root cause", "dynamic bottleneck", "system behavior", "diagnostics"]),
    c("art.shared_resource.model", "Shared-resource process-performance model", "formal_model", "2023", ["expert.vadim_denisov", DIRK], ["src.shared.resources"], "resource_performance", "Separate process behavior from contention for shared resources.", ["resource", "work item", "queue", "service episode", "allocation"], ["correlate", "decompose", "infer queue"], ["event-data resource analysis"], ["resource interactions are explicitly modeled"], ["resource events are observable"], ["unobserved work and preemption limit inference"], ["resource mining", "queueing", "performance"]),
    c("art.queue.inference", "Queue inference from object-centric event data", "analytical_method", "2023", ["expert.vadim_denisov", DIRK], ["src.shared.resources"], "queue_diagnostics", "Infer waiting populations and queue disciplines when queues are not directly logged.", ["arrival event", "service start", "completion", "resource", "candidate queue"], ["infer arrival", "infer departure", "rank discipline hypothesis"], ["event-correlation and temporal reconstruction"], ["inferred queue carries assumptions and provenance"], ["event semantics approximate arrivals and service"], ["queue state is latent and may be non-identifiable"], ["queueing", "diagnostics", "inference"]),
    c("art.preprocessing.reference_model", "Event-log preparation reference pipeline", "methodology", "2022-11-08", [DIRK], ["src.preprocessing"], "event_data_preparation", "Separate extraction, correlation, abstraction, filtering, and quality decisions before mining.", ["source record", "event", "case/object correlation", "activity", "timestamp", "log"], ["extract", "correlate", "abstract", "filter", "validate"], ["staged preparation workflow"], ["preparation choices can be documented"], ["source access and domain experts exist"], ["prepared logs are constructed analytical artifacts, not raw truth"], ["data engineering", "event-log preparation", "methodology"]),
    c("art.preprocessing.correlation", "Event correlation decision", "operation", "2022", [DIRK], ["src.preprocessing", "src.oced.symposium"], "event_data_preparation", "Assign events to cases or objects without hiding the construction rule.", ["event candidate", "identifier", "object", "correlation evidence"], ["match", "infer", "refuse", "record provenance"], ["rule-based correlation"], ["observed and inferred correlation are distinguishable"], ["identifier semantics are known"], ["wrong correlation invalidates downstream behavior"], ["correlation", "identity", "data quality"]),
    c("art.preprocessing.activity_abstraction", "Activity abstraction decision", "operation", "2022", [DIRK], ["src.preprocessing", "src.abstraction.paper"], "event_data_preparation", "Map low-level source events to activities at a declared semantic level.", ["source event type", "activity class", "mapping", "residual"], ["classify", "merge", "split", "retain residual"], ["declarative abstraction"], ["mapping is versioned and replayable"], ["source event meaning is understood"], ["many-to-one abstraction can erase behavior"], ["abstraction", "semantic mapping", "information loss"]),
    c("art.abstraction.df_information", "Information analysis of directly-follows abstraction", "formal_analysis", "2019", [LEEMANS, DIRK], ["src.abstraction.paper", "src.abstraction.repo"], "process_discovery_theory", "Determine what behavioral information directly-follows abstraction preserves and loses.", ["event log", "directly-follows abstraction", "process tree", "behavioral relation"], ["abstract", "compare information", "test rediscoverability"], ["formal and experimental abstraction analysis"], ["preservation claims are stated for explicit model/log classes"], ["assumptions of the studied abstraction hold"], ["directly-follows is not universally information preserving"], ["process discovery", "information loss", "formal guarantee"]),
    c("art.abstraction.experiment", "Information-preservation experiment harness", "benchmark", "2019", [LEEMANS, DIRK], ["src.abstraction.repo"], "benchmarking", "Reproduce comparison of miners and abstractions over named event logs.", ["event-log corpus", "miner configuration", "process-tree analysis", "result"], ["configure", "run", "compare"], ["Java experiment harness"], ["named inputs and code are published"], ["legacy dependencies remain executable"], ["benchmark corpus and tool editions age"], ["benchmark", "reproducibility", "tool qualification"]),
    c("art.scalable.divide_conquer", "Divide-and-conquer process discovery", "algorithm", "2018", [LEEMANS, DIRK, WIL], ["src.scalable.paper", "src.decomposition"], "process_discovery", "Scale discovery by decomposing event data and composing results.", ["event log", "decomposition", "sublog", "partial model", "composed model"], ["partition", "discover", "compose"], ["decomposed discovery"], ["guarantees depend on valid decomposition and miner"], ["decomposition interfaces preserve relevant behavior"], ["boundary behavior can be lost or miscomposed"], ["scalability", "process discovery", "composition"]),
    c("art.scalable.conformance", "Decomposed conformance checking", "algorithm", "2018", [LEEMANS, DIRK, WIL], ["src.scalable.paper", "src.decomposition"], "conformance_checking", "Scale conformance by decomposing model/log comparison.", ["event log", "process model", "decomposition", "local conformance result"], ["decompose", "check", "aggregate"], ["decomposed conformance"], ["aggregate result is valid under stated decomposition conditions"], ["interfaces satisfy composition conditions"], ["local fitness summaries can hide global synchronization deviations"], ["scalability", "conformance", "composition"]),
    c("art.robust.guarantee_catalog", "Process-discovery guarantee catalog", "theory", "2017", [LEEMANS, DIRK], ["src.robust.thesis"], "process_discovery_theory", "Make soundness, fitness, precision, completeness, and rediscoverability obligations explicit.", ["event log", "process model", "language", "quality criterion", "guarantee"], ["define", "prove", "falsify"], ["formal analysis of discovery methods"], ["illegal or unsound result states can be rejected"], ["formal event/model semantics"], ["guarantees are conditional, not universal product claims"], ["formal guarantees", "process discovery", "proof obligation"]),
    c("art.inductive.miner", "Inductive Miner", "algorithm", "2013", [LEEMANS, DIRK, WIL], ["src.inductive.miner", "src.robust.thesis"], "process_discovery", "Discover block-structured process models while guaranteeing soundness.", ["event log", "directly-follows graph", "process-tree cut", "process tree", "Petri net"], ["detect cut", "split log", "recurse", "fall through"], ["recursive inductive discovery"], ["sound block-structured output"], ["event log and fall-through policy"], ["noise handling and rediscoverability vary by variant"], ["process discovery", "algorithm", "soundness"]),
    c("art.precision.measure_audit", "Audit of process-mining precision measures", "measure_analysis", "2017-05-09", [DIRK, WIL], ["src.precision.paper"], "evaluation", "Show that precision measures with the same name can disagree and have counterintuitive properties.", ["event log", "process model", "precision measure", "axiom", "ranking"], ["score", "compare", "test axiom"], ["measure comparison and counterexamples"], ["counterexamples falsify universal interchangeability"], ["models and logs match measure domains"], ["one numeric precision score is not semantic truth"], ["evaluation", "metric", "counterexample"]),
    c("art.artifact.lifecycle_discovery", "Artifact lifecycle discovery", "algorithm", "2015", [DIRK], ["src.artifact.lifecycle"], "process_discovery", "Reverse-engineer lifecycle models for business artifacts from event data.", ["artifact", "artifact event", "lifecycle state", "artifact-centric model"], ["correlate", "discover lifecycle", "compose"], ["artifact-centric lifecycle discovery"], ["output lifecycle has explicit model semantics"], ["artifact identity and events are available"], ["artifact boundaries and interactions may be incomplete"], ["artifact-centric mining", "lifecycle", "process discovery"]),
    c("art.erp.interacting_artifacts", "Interacting-artifact discovery from ERP", "analytical_method", "2016", [DIRK, "expert.xixi_lu"], ["src.erp.artifacts"], "erp_process_mining", "Analyze O2C-like ERP behavior with multiple interrelated business documents.", ["sales order", "item", "shipment", "invoice", "event", "interaction"], ["extract", "correlate per artifact", "discover", "link"], ["multi-artifact discovery"], ["distinct artifact identifiers and interactions are retained"], ["ERP record semantics are mapped correctly"], ["ERP customizations and missing relations limit portability"], ["ERP", "object-centric process mining", "business objects"]),
    c("art.sixsigma.pmss", "Process Mining for Six Sigma guideline", "methodology", "2021", [DIRK], ["src.sixsigma"], "process_improvement", "Integrate process-mining evidence into DMAIC improvement work.", ["DMAIC phase", "process question", "event log", "analysis result", "improvement action"], ["define", "measure", "analyze", "improve", "control"], ["PMSS guideline"], ["method stages and tool support are explicit"], ["organizational improvement process follows DMAIC"], ["analysis evidence does not guarantee intervention effect"], ["process improvement", "methodology", "decision support"]),
    c("art.process_context.domain_extension", "Process-mining extension of a domain data model", "formal_model", "2026", ["expert.ava_swevels", "expert.francesca_zerbato", DIRK], ["src.process_context"], "domain_context_process_mining", "Apply generic process-mining concepts while retaining the original domain vocabulary and model.", ["domain-specific type", "generic process-mining type", "generalization relation", "domain instance", "analysis result"], ["extend type model", "generalize", "apply generic technique", "write back result"], ["typed domain-model extension"], ["domain concepts remain available when process-mining abstractions and results are added"], ["generalization links correctly express process-mining roles"], ["one benchmark analysis does not establish all domain-model or technique combinations"], ["domain model", "object-centric semantics", "iterative analysis", "compiler front-end"]),
    c("art.process_context.iterative_enrichment", "Domain-context iterative analysis and enrichment", "methodology", "2026", ["expert.ava_swevels", "expert.francesca_zerbato", DIRK], ["src.process_context"], "domain_context_process_mining", "Avoid repeated mental translation between generic process-mining results and domain concepts.", ["domain data", "process-mining question", "generic technique", "domain-grounded result", "enriched data"], ["select domain types", "analyze", "enrich", "iterate"], ["domain-context analysis workflow"], ["results are attached to the same governed domain model used for the question"], ["analysis result types can be represented without corrupting source facts"], ["analytical enrichment must remain distinct from operational source truth"], ["iterative analysis", "domain semantics", "result provenance"]),
    c("art.filter_branch_map.model", "FilterBranchMap", "analytical_representation", "2026", ["expert.laura_didden", DIRK, "expert.francesca_zerbato"], ["src.filter_branch_map"], "exploratory_analysis_provenance", "Make successive filters, included/excluded subsets, and analytical perspectives retraceable.", ["filter step", "parent subset", "included subset", "excluded subset", "branch", "analytical perspective"], ["apply filter", "branch", "compare", "retrace"], ["filter-branch provenance construction"], ["subset construction and relationships are externalized"], ["filter predicates and input snapshot are retained"], ["qualitative user study and one Sepsis log do not prove general usability"], ["exploratory analysis", "provenance", "visual analytics"]),
    c("art.filter_branch_map.provenance", "Exploratory filter-step provenance", "evidence_contract", "2026", ["expert.laura_didden", DIRK, "expert.francesca_zerbato"], ["src.filter_branch_map"], "exploratory_analysis_provenance", "Preserve why an exploratory subset exists and what was excluded at each step.", ["input snapshot", "filter predicate", "filter parameters", "included IDs", "excluded IDs", "parent operation"], ["record", "replay", "compare", "invalidate"], ["deterministic filter replay"], ["filter lineage is explicit when input identity and predicate edition are retained"], ["filter operation is deterministic or records nondeterminism"], ["visual provenance does not replace exact machine-readable operation lineage"], ["lineage", "exploration", "information loss"]),
    c("art.queue_ocel.object_model", "Queue and worker object-centric event model", "formal_model", "2026", ["expert.sander_van_gansewinkel", "expert.vadim_denisov", DIRK], ["src.queue_object_centric"], "queue_diagnostics", "Represent queues and workers as objects so missing queue behavior can be reconstructed.", ["queue object", "worker object", "work-item object", "enqueue hypothesis", "dequeue/service event"], ["objectify queue", "correlate worker", "infer missing queue relation"], ["object-centric queue reconstruction"], ["inferred queue facts remain distinguishable from observed events"], ["incident-management records expose sufficient temporal and worker evidence"], ["evaluation establishes feasibility in one industrial incident-management process"], ["queueing", "object-centric semantics", "data quality"]),
    c("art.queue_ocel.inference", "Object-centric queue-information inference", "algorithm", "2026", ["expert.sander_van_gansewinkel", "expert.vadim_denisov", DIRK], ["src.queue_object_centric"], "queue_diagnostics", "Restore latent queue entries, exits, and ordering from object-centric event evidence.", ["OCEL", "queue object", "worker object", "candidate queue episode", "inference provenance"], ["infer", "order", "attach confidence", "refuse"], ["object-centric queue inference"], ["outputs can be inspected as inferred event/object relations"], ["queue model and event semantics fit the operational process"], ["latent queue history may be non-identifiable; alternative reconstructions must be retained"], ["queue inference", "partiality", "diagnostics"]),
    c("art.oced_pg.research_dataset", "OCED-PG semantic-header research corpus", "dataset", "2023-08-29", ["expert.ava_swevels", DIRK], ["src.oced_pg_dataset"], "benchmark_data", "Provide executable source records, dataset descriptions, and semantic headers for six datasets.", ["BPIC source dataset", "dataset-description JSON", "semantic-header JSON", "EKG output", "PromG v0.1.25 occurrence"], ["load", "compile header", "construct EKG", "compare"], ["OCED-PG transformation"], ["six named datasets and exact implementation occurrence are published"], ["PromG v0.1.25 and query repositories remain available"], ["artifact is version-bound and does not independently qualify newer runtimes"], ["dataset", "semantic mapping", "conformance fixture"]),
    c("art.object_centric_case.design_space", "Object-centric case design space", "design_space", "2026", [DIRK, "expert.marco_montali"], ["src.object_centric_case_2026"], "case_construction", "Explore case definitions when shared objects prevent behavior from partitioning into independent executions.", ["shared object", "behavioral boundary", "case candidate", "execution overlap", "analysis question"], ["define candidate", "compare", "select", "permit overlap"], ["case-definition exploration"], ["case choice is treated as an analytical decision rather than an intrinsic field"], ["question and intended method determine useful boundaries"], ["no single case definition is established as universal"], ["case construction", "object-centric semantics", "decision space"]),
    c("art.xes.standard", "XES event-log standard", "standard", "2016", [WIL], ["src.xes.standard", "src.process.manifesto"], "event_log_exchange", "Exchange case-centric event logs with extensible attributes.", ["log", "trace", "event", "attribute", "extension", "classifier"], ["serialize", "parse", "classify"], ["XML exchange"], ["standardized structure and extension mechanism"], ["single-trace/case organization is appropriate"], ["XES trace structure is not object-centric OCED"], ["standard", "event log", "exchange"]),
    c("art.prom.framework", "ProM framework", "tool_platform", "ongoing", [WIL, DIRK], ["src.prom"], "process_mining_tooling", "Host interoperable importers, miners, conformance checkers, and visualizers as plugins.", ["plugin", "typed artifact", "connection", "workspace", "event log", "process model"], ["import", "invoke plugin", "connect result", "export"], ["plugin execution framework"], ["plugin provenance and types can be recorded"], ["Java runtime and plugin compatibility"], ["platform plugin is not a pure library and individual plugin quality varies"], ["tool platform", "plugin", "runtime"]),
    c("art.pm4py.library", "PM4Py process-mining library", "library", "ongoing", [BERTI, WIL], ["src.pm4py", "src.ocpa.repo"], "process_mining_tooling", "Expose event-data import, discovery, conformance, object-centric, and analysis methods as Python APIs.", ["event log", "dataframe", "process model", "OCEL", "algorithm parameters"], ["import", "discover", "check", "analyze", "export"], ["Python algorithm implementations"], ["open implementation and tests enable qualification"], ["version-specific API contracts"], ["library API does not make every method semantically interchangeable"], ["library", "runtime", "adapter"]),
    c("art.alignment.classic", "Optimal alignment of observed and modeled behavior", "conformance_method", "2013", [WIL], ["src.alignment.repair"], "conformance_checking", "Find a minimum-cost explanation of deviations between a trace and model execution.", ["trace", "model run", "synchronous move", "log move", "model move", "cost"], ["synchronize", "insert", "skip", "minimize"], ["shortest-path/A-star alignment"], ["optimal relative to move-cost function and completed search"], ["finite reachable state or appropriate bounds"], ["cost choices encode judgment; timeout can yield partial result"], ["conformance", "optimization", "diagnostics"]),
    c("art.model.repair", "Process-model repair", "algorithm", "2012", [DIRK, WIL], ["src.model.repair"], "model_enhancement", "Alter a reference model to better reflect observed behavior while controlling change.", ["process model", "event log", "deviation", "repair edit", "repaired model"], ["align", "locate deviation", "edit", "validate"], ["alignment-guided repair"], ["repair relation to original and log is measurable"], ["repair objective and allowed edits are declared"], ["fitness improvement can reduce precision or violate stakeholder intent"], ["model repair", "conformance", "change"]),
    c("art.proclet.synchronous", "Synchronous proclet model", "formal_model", "2010", [DIRK], ["src.proclets"], "behavioral_model", "Model interacting artifact lifecycles with explicit synchronization.", ["proclet", "port", "channel", "synchronization", "artifact instance"], ["compose", "synchronize", "execute"], ["proclet execution semantics"], ["local behavior and interaction are distinct"], ["interaction events are observable or modeled"], ["model expressiveness and discovery cost trade off"], ["behavioral model", "composition", "synchronization"]),
]


# Add separately typed exchange, lifecycle, evidence, and implementation contributions.
DERIVED_SPECS = [
    ("oced.event_identity", "OCED event identity contract", "value_object", "event_data_standardization", "event identity is stable and distinct from event type", "src.oced.report"),
    ("oced.object_identity", "OCED object identity contract", "value_object", "event_data_standardization", "object identity is stable within its declared scope", "src.oced.report"),
    ("oced.qualifier", "OCED relationship qualifier", "value_object", "event_data_standardization", "relationship role is explicit rather than inferred from endpoints", "src.oced.report"),
    ("oced.extension", "OCED extension boundary", "extension_contract", "event_data_standardization", "extensions cannot silently redefine core concepts", "src.oced.report"),
    ("oced.convention", "OCED usage convention", "convention", "event_data_standardization", "conventions remain distinguishable from normative core", "src.oced.report"),
    ("semantic_header.dataset_description", "Semantic-header dataset description", "schema", "event_data_preparation", "source columns and carrier types are declared", "src.oced.symposium"),
    ("semantic_header.mapping_rule", "Semantic-header transformation rule", "mapping_contract", "event_data_preparation", "record-to-semantic mapping is executable and reviewable", "src.oced.promg.docs"),
    ("tekg.snapshot", "tEKG entity snapshot", "value_object", "temporal_event_data", "attribute state is materialized at a time boundary", "src.tekg.paper"),
    ("tekg.snapshot_successor", "tEKG snapshot succession", "relation_semantics", "temporal_event_data", "snapshot order is explicit", "src.tekg.paper"),
    ("tekg.df_pruning", "tEKG directly-follows pruning", "algorithm", "temporal_event_data", "redundant derived directly-follows edges are removed by stated rules", "src.tekg.paper"),
    ("process_execution.extraction", "Process-execution extraction operator", "query_operator", "case_construction", "case-like graph boundaries are parameterized", "src.process.executions"),
    ("process_variant.isomorphism", "Object-centric variant isomorphism", "algorithm", "variant_analysis", "variant equivalence is label-relative", "src.process.executions"),
    ("saocpm.state_transition_event", "Object state-transition event", "domain_event", "state_aware_ocpm", "prior and new state are explicit", "src.saocpm.paper"),
    ("saocpm.state_refined_activity", "State-refined activity type", "representation", "state_aware_ocpm", "activity and state dimensions remain separable", "src.saocpm.paper"),
    ("saocpm.coalesced_ocel", "Coalesced State-Aware OCEL", "formal_model", "state_aware_ocpm", "coalescing is a separate representation decision from state-change event generation", "src.saocpm.paper"),
    ("performance.segment", "Performance-spectrum segment", "value_object", "performance_analysis", "a case flow between two steps retains start and end time", "src.performance.paper"),
    ("performance.classifier", "Performance-spectrum classifier", "policy", "performance_analysis", "classification thresholds and functions are exposed", "src.performance.repo"),
    ("performance.session", "Performance-spectrum session artifact", "artifact", "performance_analysis", "derived data and configuration are versioned together", "src.performance.repo"),
    ("task.execution", "Task execution graph object", "formal_object", "task_behavior_analysis", "multi-event work instance is distinct from activity type", "src.task.pattern.paper"),
    ("task.routine", "Task routine graph pattern", "formal_object", "task_behavior_analysis", "repetition across task executions is explicitly classified", "src.task.pattern.paper"),
    ("missing_id.hypothesis", "Inferred entity-identity hypothesis", "hypothesis", "event_data_quality", "inference never becomes observed identity without adjudication", "src.missing.identifiers"),
    ("ocpn.variable_arc", "OCPN variable arc", "formal_object", "behavioral_model", "multiplicity behavior is explicit", "src.ocpn.discovery"),
    ("alignment.move", "Conformance alignment move", "formal_object", "conformance_checking", "synchronous/log/model moves have explicit costs", "src.alignment.repair"),
    ("alignment.refusal", "Conformance solver partial-result contract", "failure_contract", "conformance_checking", "timeout and unknown are not reported as optimum", "src.ocpi.alignments"),
    ("discovery.cut", "Inductive-miner process-tree cut", "formal_object", "process_discovery", "cut type and partition are explicit", "src.inductive.miner"),
    ("discovery.fallthrough", "Inductive-miner fall-through policy", "policy", "process_discovery", "fallback behavior is exposed", "src.inductive.miner"),
    ("quality.precision_axiom", "Precision-measure axiom test", "law_oracle", "evaluation", "metric behavior is tested against stated axioms", "src.precision.paper"),
    ("preparation.provenance", "Event-log preparation provenance", "evidence_contract", "event_data_preparation", "each derived event can trace to source and rule", "src.preprocessing"),
    ("preparation.residual", "Preparation information-loss residual", "evidence_contract", "event_data_preparation", "filtered or merged information is accounted for", "src.abstraction.paper"),
    ("xes.classifier", "XES event classifier", "policy", "event_log_exchange", "event-class identity is a declared function over attributes", "src.xes.standard"),
    ("prom.plugin_contract", "ProM plugin contract", "runtime_contract", "process_mining_tooling", "typed inputs, outputs, and connections are declared", "src.prom"),
    ("pm4py.algorithm_parameters", "PM4Py algorithm parameter contract", "runtime_contract", "process_mining_tooling", "algorithm defaults and version are part of reproducibility", "src.pm4py"),
    ("pmss.phase_binding", "PMSS analysis-to-DMAIC binding", "methodology_component", "process_improvement", "analysis methods are selected by improvement question", "src.sixsigma"),
]

DERIVED_AUTHORS_BY_SOURCE = {
    "src.oced.report": [DIRK, "expert.marco_montali", WIL],
    "src.oced.symposium": [DIRK, "expert.ava_swevels"],
    "src.oced.promg.docs": [DIRK, "expert.ava_swevels"],
    "src.tekg.paper": ["expert.shahrzad_khayatbashi", "expert.olaf_hartig", "expert.amin_jalali"],
    "src.process.executions": ["expert.jan_niklas_adams", LEEMANS, WIL],
    "src.saocpm.paper": ["expert.dina_kretzschmann", BERTI, WIL],
    "src.performance.paper": ["expert.vadim_denisov", DIRK, WIL],
    "src.performance.repo": ["expert.vadim_denisov", DIRK],
    "src.task.pattern.paper": ["expert.eva_klijn", "expert.felix_mannhardt", DIRK],
    "src.missing.identifiers": ["expert.ava_swevels", DIRK],
    "src.ocpn.discovery": [BERTI, WIL],
    "src.alignment.repair": [WIL],
    "src.ocpi.alignments": ["expert.marco_montali"],
    "src.inductive.miner": [LEEMANS, DIRK, WIL],
    "src.precision.paper": [DIRK, WIL],
    "src.preprocessing": [DIRK],
    "src.abstraction.paper": [LEEMANS, DIRK],
    "src.xes.standard": [WIL],
    "src.prom": [WIL],
    "src.pm4py": [BERTI],
    "src.sixsigma": [DIRK],
}
for key, name, kind, context, guarantee, sid in DERIVED_SPECS:
    CONTRIBUTIONS.append(c(
        f"art.{key}", name, kind, "see-primary-source", DERIVED_AUTHORS_BY_SOURCE[sid],
        [sid], context, guarantee, [name, "declared identity", "evidence reference"],
        ["construct", "validate", "serialize"], ["deterministic contract operation"], [guarantee],
        ["primary source semantics apply"], ["scope is bounded by the cited artifact"], [context, "compiler contract"]
    ))


EXPERT_NAME = {eid: name for eid, name, _orcid, _areas in EXPERTS}
KEY_BYLINES = {
    "art.oced.core_metamodel": ["Dirk Fahland", "Marco Montali", "Julian Lebherz", "Wil M. P. van der Aalst", "Maarten van Asseldonk", "Peter Blank", "Lien Bosmans", "Marcus Brenscheidt", "Claudio Di Ciccio", "Andrea Delgado", "Daniel Calegari", "Jari Peeperkorn", "Eric Verbeek", "Lotte Vugs", "Moe Thandar Wynn"],
    "art.oced.design_space": ["Dirk Fahland", "Marco Montali", "Julian Lebherz", "Wil M. P. van der Aalst", "Maarten van Asseldonk", "Peter Blank", "Lien Bosmans", "Marcus Brenscheidt", "Claudio Di Ciccio", "Andrea Delgado", "Daniel Calegari", "Jari Peeperkorn", "Eric Verbeek", "Lotte Vugs", "Moe Thandar Wynn"],
    "art.hoeg.encoding": ["Tim K. Smit", "Hajo A. Reijers", "Xixi Lu"],
    "art.hoeg.predictor": ["Tim K. Smit", "Hajo A. Reijers", "Xixi Lu"],
    "art.tekg.model": ["Shahrzad Khayatbashi", "Olaf Hartig", "Amin Jalali"],
    "art.tekg.transform": ["Shahrzad Khayatbashi", "Olaf Hartig", "Amin Jalali"],
    "art.tekg.dataset": ["Shahrzad Khayatbashi", "Olaf Hartig", "Amin Jalali"],
    "art.saocpm.state_semantics": ["Dina Kretzschmann", "Alessandro Berti", "Wil M. P. van der Aalst"],
    "art.saocpm.discovery": ["Dina Kretzschmann", "Alessandro Berti", "Wil M. P. van der Aalst"],
    "art.dynamic_bottleneck.system_event": ["Zahra Toosinezhad", "Dirk Fahland", "Özge Köroğlu", "Wil M. P. van der Aalst"],
    "art.dynamic_bottleneck.cascade": ["Zahra Toosinezhad", "Dirk Fahland", "Özge Köroğlu", "Wil M. P. van der Aalst"],
    "art.dynamic_bottleneck.predecessor_patterns": ["Zahra Toosinezhad", "Dirk Fahland", "Özge Köroğlu", "Wil M. P. van der Aalst"],
}
ROLE_OVERRIDES = {
    "art.shared_resource.model": {"expert.vadim_denisov": "author", DIRK: "supervisor"},
    "art.queue.inference": {"expert.vadim_denisov": "author", DIRK: "supervisor"},
    "art.performance.miner": {"expert.vadim_denisov": "developer", "expert.elena_belkina": "developer", DIRK: "developer"},
}
for contribution in CONTRIBUTIONS:
    contribution["bibliographic_authors"] = KEY_BYLINES.get(
        contribution["id"],
        [EXPERT_NAME.get(eid, eid) for eid in contribution["authors_or_maintainers"]],
    )
    role = "author"
    if contribution["artifact_kind"] == "tool":
        role = "developer"
    elif contribution["artifact_kind"] in {"library", "tool_platform"}:
        role = "maintainer"
    contribution["expert_roles"] = [
        {"expert_id": eid, "role": ROLE_OVERRIDES.get(contribution["id"], {}).get(eid, role)}
        for eid in contribution["authors_or_maintainers"]
    ]


LIBRARY_TEMPLATES = {
    "pure": "Pure semantic types and total/partial operations; no I/O or vendor SDK.",
    "runtime": "Executable algorithm with explicit resource, cancellation, and failure contracts.",
    "adapter": "Format, database, or tool boundary; preserves exact edition and provenance.",
    "test": "Law or conformance oracle with fixtures and negative twins.",
}


def mappings_for(rec):
    cats = rec["categories"]
    context = rec["bounded_context"]
    kind = rec["artifact_kind"]
    out = []
    targets = [
        ("practice", f"practice.process_mining.{cats[0].replace(' ', '_') if cats else context}"),
        ("operation", f"operation.{context}.{rec['operators'][0].replace(' ', '_')}"),
        ("representation", f"representation.{context}.{rec['formal_objects_or_types'][0].replace(' ', '_')}"),
        ("compiler_node", f"compiler.artifact.{kind}"),
    ]
    if kind in {"algorithm", "conformance_method", "analytical_method", "transformation", "query_operator"}:
        targets.append(("method", f"method.process_mining.{rec['id'].removeprefix('art.')}"))
        targets.append(("kernel", f"kernel.{context}.{rec['algorithms'][0].replace(' ', '_')}"))
    if kind in {"tool", "library", "tool_platform", "exchange_format"}:
        targets.append(("library", f"library.process_mining.{rec['id'].removeprefix('art.')}"))
    for ix, (mk, target) in enumerate(targets):
        out.append({
            "id": f"map.{rec['id'].removeprefix('art.')}.{ix:02d}",
            "artifact_id": rec["id"],
            "mapping_kind": mk,
            "canonical_target": target,
            "relation": "candidate_realizes" if mk in {"method", "kernel", "library"} else "candidate_refines",
            "decision_or_proof": rec["exposed_decisions"][0],
            "primary_source_ids": rec["primary_source_ids"],
            "adjudication_status": {
                "core_candidate": "candidate_requires_global_binding",
                "reference_only_noncore": "reference_only_no_binding",
                "excluded_ai_method": "excluded_noncore_reference",
            }.get(rec["status"], "candidate_requires_global_binding"),
        })
    return out


def library_records(rec):
    if rec["status"] != "core_candidate":
        return []
    slug = rec["id"].removeprefix("art.")
    records = []
    kinds = ["pure", "test"]
    if rec["artifact_kind"] in {"algorithm", "tool", "library", "tool_platform", "conformance_method", "analytical_method", "transformation", "query_operator"}:
        kinds.append("runtime")
    if rec["artifact_kind"] in {"exchange_format", "tool", "tool_platform", "dataset", "dataset_registry", "transformation"}:
        kinds.append("adapter")
    for lk in kinds:
        records.append({
            "id": f"lib.{slug}.{lk}",
            "artifact_id": rec["id"],
            "library_kind": lk,
            "responsibility": LIBRARY_TEMPLATES[lk],
            "public_surface": [rec["formal_objects_or_types"][0], rec["operators"][0]],
            "must_not_own": ["foreign vendor semantics", "business-domain policy outside the bounded context"],
            "exposed_decisions": rec["exposed_decisions"],
            "source_ids": rec["primary_source_ids"],
        })
    return records


REVIEW_QUEUE = [
    {"id": "review.hoeg", "raw_claim": "Dirk Fahland has HOEG", "status": "resolved_misattribution", "candidate_artifact_ids": ["art.hoeg.encoding", "art.hoeg.predictor"], "finding": "HOEG means Heterogeneous Object Event Graph; primary publication authors are Tim K. Smit, Hajo A. Reijers, and Xixi Lu. It is not a Fahland artifact.", "source_ids": ["src.hoeg.paper", "src.hoeg.publisher"]},
    {"id": "review.tekgm", "raw_claim": "TEKGM", "status": "ambiguous_probable_typo", "candidate_artifact_ids": ["art.tekg.model", "art.ekg.model"], "finding": "No primary process-mining artifact with acronym TEKGM was verified. The closest supported identities are EKG and temporal Event Knowledge Graph (tEKG); do not alias automatically.", "source_ids": ["src.tekg.paper", "src.ekg.paper"]},
    {"id": "review.tekg_collision", "raw_claim": "TEKG / temporal event knowledge graph", "status": "resolved_name_collision", "candidate_artifact_ids": ["art.tekg.model"], "finding": "The process-mining tEKG of Khayatbashi, Hartig, and Jalali is distinct from the TEKG constructed inside TEILP for temporal-knowledge-graph time prediction. Same/near acronym does not imply shared formal model.", "source_ids": ["src.tekg.paper", "src.teilp.paper"]},
    {"id": "review.sa_ocel", "raw_claim": "SA-OCEL / State-Aware OCEL", "status": "resolved_with_name_guard", "candidate_artifact_ids": ["art.saocpm.state_semantics", "art.saocpm.coalesced_ocel"], "finding": "Definition 2 in the verified SA-OCPM paper formally names a State-Aware OCEL. SA-OCPM is the method/framework; State-Aware OCEL is its derived log model. Neither is an OCEL standard edition.", "source_ids": ["src.saocpm.paper", "src.ocel2.site"]},
    {"id": "review.oced", "raw_claim": "OCED", "status": "resolved_with_status_guard", "candidate_artifact_ids": ["art.oced.core_metamodel", "art.oced.design_space"], "finding": "OCED is a community standardization effort/core model and design space. It must not be collapsed into OCEL 2.0, OCED-PG, a tool, or a final IEEE standard edition.", "source_ids": ["src.oced.report", "src.oced.wg", "src.ocel2.paper"]},
    {"id": "review.oced_pg", "raw_claim": "OCED-PG", "status": "resolved", "candidate_artifact_ids": ["art.oced.pg_base_ontology", "art.oced.pg_reference_ontology", "art.oced.pg_elt"], "finding": "OCED-PG is a property-graph reference implementation and declarative ELT framework around base/reference ontologies and semantic-header mappings, not the OCED abstract model itself.", "source_ids": ["src.oced.promg.docs", "src.oced.promg.repo"]},
    {"id": "review.expert_ownership", "raw_claim": "an expert has an artifact", "status": "constitutional_rule", "candidate_artifact_ids": [], "finding": "Authorship, supervision, maintenance, working-group leadership, implementation, and conceptual influence are different roles and must be stored separately.", "source_ids": ["src.fahland.profile", "src.fahland.publications"]},
]


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def write_jsonl(path, records):
    path.write_text("".join(canonical_json(r) + "\n" for r in sorted(records, key=lambda x: x["id"])))


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    mappings = [m for rec in CONTRIBUTIONS for m in mappings_for(rec)]
    libraries = [lib for rec in CONTRIBUTIONS for lib in library_records(rec)]
    by_expert = defaultdict(list)
    for rec in CONTRIBUTIONS:
        for expert in rec["authors_or_maintainers"]:
            by_expert[expert].append(rec["id"])
    expert_records = [{
        "id": eid,
        "name": name,
        "orcid": orcid,
        "expertise_claims": expertise,
        "contribution_ids": sorted(by_expert[eid]),
        "role_warning": "Contribution relation denotes the role stated on the artifact; never infer ownership of adjacent artifacts.",
    } for eid, name, orcid, expertise in EXPERTS]
    gaps = {
        "edition": EDITION,
        "gaps": [
            "Complete publication-by-publication adjudication of all 166 TU/e-listed Fahland outputs is not claimed.",
            "TEKGM remains unresolved and must not be auto-aliased to tEKG.",
            "State-Aware OCEL is verified as Definition 2 inside SA-OCPM, but not as a normative OCEL standard edition.",
            "Many empirical methods lack independent cross-tool, cross-domain, and resource-envelope qualification.",
            "Object-centric case construction, temporal relationship semantics, data-quality fitness, and conformance remain active research boundaries.",
            "Tool repositories need commit-SHA, dependency, license, target, and benchmark requalification before binding.",
            "Expert portfolio coverage is a falsification pilot, not a global expert census.",
        ],
        "non_collapsible_laws": [
            "paper acronym != method != formal model != encoding != algorithm != trained model != tool != standard",
            "authorship != supervision != maintenance != standardization leadership != artifact ownership",
            "OCED != OCEL 2.0 != OCED-PG != EKG != tEKG",
            "event != activity type; object != object type; identity != correlation hypothesis",
            "process execution != universal case; variant equality is parameterized",
            "discovery != conformance != diagnostics != root-cause proof != performance analysis != prediction",
            "anomaly != defect; deviation != violation; bottleneck signature != causal explanation",
            "format validity != semantic validity != data quality != fitness for an analytical question",
            "algorithm guarantee != implementation qualification != provider offer",
        ],
    }
    write_jsonl(ROOT / "sources.jsonl", SOURCES)
    write_jsonl(ROOT / "experts.jsonl", expert_records)
    write_jsonl(ROOT / "contributions.jsonl", CONTRIBUTIONS)
    write_jsonl(ROOT / "canonical-mappings.jsonl", mappings)
    write_jsonl(ROOT / "library-boundaries.jsonl", libraries)
    write_jsonl(ROOT / "review-queue.jsonl", REVIEW_QUEUE)
    write_json(ROOT / "coverage-gaps.json", gaps)
    outputs = ["sources.jsonl", "experts.jsonl", "contributions.jsonl", "canonical-mappings.jsonl", "library-boundaries.jsonl", "review-queue.jsonl", "coverage-gaps.json"]
    digest = hashlib.sha256("".join((ROOT / name).read_text() for name in outputs).encode()).hexdigest()
    manifest = {
        "edition": EDITION,
        "generated_on": RETRIEVED,
        "record_counts": {
            "sources": len(SOURCES),
            "primary_sources": sum(s["is_primary_evidence"] for s in SOURCES),
            "experts": len(expert_records),
            "contributions": len(CONTRIBUTIONS),
            "canonical_mappings": len(mappings),
            "library_boundaries": len(libraries),
            "review_items": len(REVIEW_QUEUE),
        },
        "contribution_kinds": dict(sorted(Counter(r["artifact_kind"] for r in CONTRIBUTIONS).items())),
        "bounded_contexts": dict(sorted(Counter(r["bounded_context"] for r in CONTRIBUTIONS).items())),
        "content_sha256": digest,
        "generator": "build_corpus.py",
        "validator": "validate.py",
        "claim": "falsification pilot; not exhaustive global expert census",
    }
    write_json(ROOT / "manifest.json", manifest)
    print(json.dumps(manifest["record_counts"], sort_keys=True))


if __name__ == "__main__":
    main()
