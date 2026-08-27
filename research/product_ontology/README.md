# Sovereign product ontology

This directory derives the product portfolio for a composable enterprise data and analytics
company. Product derivation is downstream of the horizontal bounded-context atlas in
`research/domain_atlas/`. It deliberately does not start from vendor packaging, repository
folders, libraries, or a fixed product count. Those are related but different decompositions.

## Governing question

> What independently adoptable, operable, evolvable and replaceable promises must the company
> make so that declared enterprise intent can be compiled into trustworthy data and analytical
> solutions without collapsing products, capabilities, semantic owners and implementations into
> one flat list?

## Current standing

```text
status                  RESEARCH_CANDIDATE
fixed product count     none
market packaging seed   about 10 suites
product-family seed     50 from the first packaging pass
global candidates       72 after twelve evidence-backed boundary passes plus the quality/reconciliation split
adjudicated candidates  72/72 in this finite edition; open-world completeness remains false
boundary verdicts       48 strong + 11 presumptive + 4 defer + 9 merge/reclassify
adjudicated slices      lakehouse + movement + governance + methods + consumption + platform + model/decision + query/warehouse/search/protection + semantic metrics/formulas + collaboration/privacy/resolution/assurance + representation/codec + analytical operations
ratified products        0
certification            NONE
full 29-field DDD        59/59 retained products
build-ready products     0; 165 blocking closure items remain explicit
```

The count is an output of domain ownership and product-boundary adjudication. A candidate is not a product merely because a
vendor sells it, an open-source project implements it, a bounded context owns related language,
or a crate contains its code.

The original `registry/` lakehouse records are a falsification pilot. The first evidence-backed
correction is in `adjudications/lakehouse/`: it splits the legacy table-management product
into contract/capability/standard/library identities, merges the unproven standalone control-plane
product into an experience capability, and retains six bounded product candidates. Four retained
global products now have complete product-specific DDD and exact product-library/compiler
attribution: managed experience, catalog, managed maintenance and data sharing. Query and
ingestion remain canonically owned by their dedicated adjudications. The environment lifecycle
maps exactly to the product-composition lifecycle contract; all physical providers and vertical
acceptance remain unqualified.

The second adjudication is in `adjudications/movement/`. It splits the generic pipeline label into
connectivity, CDC, ingestion, orchestration, dataflow, transformation-build, event-streaming and
operational-activation promises; distinguishes all cursor/checkpoint identities; and demotes
connector brands/plugins to provider offers.
Its last coarse compiler seam, activation mapping, now resolves to destination-profile compilation,
mapping-plan compilation and pure proposal evaluation. Operational authorization and execution
remain separate effect contracts.

The third adjudication is in `adjudications/governance_semantics/`. It rejects `catalog` as a
single owner; separates table commit, discovery, glossary, ontology, schema, data contract,
master/reference identity, lineage, data-quality operations, reconciliation/control operations,
policy, publication and marketplace meanings; and keeps model/agent assistance behind optional
typed proposal ports. The quality/reconciliation split contributes two full 29-field DDD dossiers,
33 exact product/library/compiler maps and explicit vertical-specialization and external-authority
seams without retaining the obsolete combined product as an alias.
Lineage and Provenance Evidence adds a third complete DDD plus eleven product-attributed libraries:
ten map to exact existing lineage contracts and the repository seam maps to an exact provider-neutral
persistence port.
Lineage paths never become causal claims, quality verdicts, audit trails or independent assurance.

The fourth adjudication is in `adjudications/analytical_methods/`. It separates business question,
analytical practice, formal method, algorithm, library, execution environment and product. It
retains only six independently supported product candidates while reclassifying statistics,
causal inference, anomaly/change, graph, text and media/signal labels as method/library families.
Models, LLMs and agents are allowed only as explicit optional or intent-required modalities over a
deterministic semantic core. Its 58 product-facing library groups and exact product libraries are projected through exact
compiler binding maps. Process mining separates OCEL/OCED, State-Aware OCEL, temporal-EKG, case,
discovery, conformance and performance contracts. Statistics, causal, forecast and anomaly/change
use independently substitutable semantic/method contracts. Graph and spatial coverage further
separates representation semantics, algorithms and kernels. Experimentation separates protocol,
assignment, randomization, exposure and immutable analysis cuts. The dedicated OR universe now
projects exact optimization and simulation libraries. Document analysis separates containers,
content graphs, parsers, layout, OCR, tables, forms, provenance, classification, extraction and
evaluation. The optional model/agent extension has explicit removable requirements and offers.
Fifteen compiler gaps—four forecast-lifecycle, three experiment-lifecycle and eight geospatial
workbench/specialized-method seams—remain explicit; every observed implementation is still unqualified.

The automation rule is intentionally stricter than "human in the loop." Models and agents may
accelerate research or propose typed artifacts, but they cannot replace vocabulary enumeration,
semantic adjudication, invariant and lifecycle definition, algorithm selection, source evidence,
negative testing, provider qualification or domain acceptance. Statistical, predictive,
heuristic, simulation and optimization methods remain ordinary first-class analytical methods;
their uncertainty and approximation must be declared and qualified without relabeling the domain
as AI.

The fifth through seventh adjudications cover analytical consumption experiences, platform/runtime
control and model/decision serving. The model/decision pass splits predictive model engineering,
feature serving, online inference, model assurance, deterministic decision execution and optional
model/agent extension runtime. It reclassifies a model registry as a lifecycle component, training
runtime as a provider, batch scoring as a dataflow composition and vector indexing as search/index
serving. Prediction remains distinct from decision, authorization, effect and outcome. The optional
extension is removable and non-authoritative.

The eighth adjudication is in `adjudications/query_warehouse_search_protection/`. It retains
analytical query execution, managed warehouse experience, virtual data access, search/index
serving, data protection/recovery and digital preservation/archive as six products. Federation is
a query capability unless a separately adopted virtual-relation lifecycle exists. Operational,
realtime and batch are workload profiles. Cache is a cross-product freshness/invalidation
contract. Vector retrieval is a search mechanism, not a feature store or ambient AI product.
Snapshots, replication and WORM storage are mechanisms; they do not prove recoverability or
preservation. All 60 library seams now resolve structurally, including exact index-mutation and
search-visibility contracts. One global removable-extension law governs optional agents and
generative models; it is not repeated as ambient AI metadata inside deterministic libraries.

The ninth adjudication is in `adjudications/semantic_metrics_formulas/`. It retains one Semantic
Metric and Formula Service while reclassifying “metric store plus query” as an overloaded
architecture/package label. Measure, metric, KPI, target, benchmark and observation remain
different identities; formula expression, definition, binding and evaluation remain separate;
semantic query is not SQL; and materialization/cache reuse requires semantic, temporal and policy
equivalence evidence. All 24 product-facing contracts project exactly to the compiler's existing
`library.smf.*` registry, but 16 semantic/conformance gaps and all provider qualifications remain
open. Optional model/agent assistance can propose or explain only; it cannot publish definitions,
authorize disclosure or replace deterministic type, fanout, summarizability and policy proofs.

The tenth adjudication is in
`adjudications/collaboration_privacy_resolution_assurance/`. It retains four independently owned
products: controlled data collaboration, privacy-rights and retention control, entity resolution,
and assurance-case appraisal. A clean room is the collaboration product promise plus selected PET
and runtime mechanisms, not a warehouse, TEE, MPC protocol or “AI” label. A match score is not a
link decision, cluster, golden record or source mutation. “Independent” is evidenced per appraisal
occurrence rather than inherited from software or a brand. Its 53 library contracts map exactly to
existing compiler libraries; all provider offers remain unqualified and 20 semantic/conformance
gaps remain blocking. Predictive ML is one entity-scoring method, while LLM/agent assistance is an
optional removable proposal surface.

The eleventh adjudication is in `adjudications/representation_codec_boundary/`. It intentionally
retains zero products: codec-as-a-service is a packaging/deployment pattern around eight reusable
representation libraries and a bounded runtime component. Carrier, serialization, framing, layout,
column encoding, compression, codec, container, loss, canonicalization and transcode remain
distinct. The global validator now refuses any template-only candidate. That is inventory closure,
not a claim that no future
product boundary can be discovered.

The first open-world inventory challenge is in
`inventory_challenges/analytical_operations_gap_audit/`. Thirty-eight primary/official sources
show five omitted jobs with enough independent user, semantic, lifecycle, operational and exit
evidence to require full adjudication: self-service data preparation, annotation/ground-truth
operations, document processing/review, visual inspection operations, and signal condition
monitoring/diagnostics. The audit decomposes 60 initial library boundaries, records five collision
rulings against existing products, retains 19 blocking gaps, and defers seven weaker hypotheses.

The twelfth adjudication is in `adjudications/analytical_operations/`. It promotes those five jobs
into the global candidate corpus only after defining five full strategic/tactical DDD dossiers,
60 product-facing library contracts and 60 exact compiler maps. Fifteen maps deliberately terminate
in blocking exact-library gaps rather than fabricated matches. All nine observed implementation
offers remain unqualified and non-portable, and 25 semantic/conformance gaps remain open. Method
results stay distinct from annotation truth, document facts, inspection disposition, machine
effects, diagnoses, prognoses, advisories and maintenance authority. Its deterministic core remains
complete without an LLM or agent; predictive, generative or agent assistance may bind only as an
explicit replaceable method/proposal port. The global corpus now contains 72 exactly adjudicated
candidates, but no product is ratified and open-world completeness remains false.

The promoted boundary challenge is in
`inventory_challenges/quality_reconciliation_split_audit/`. The dedicated 37-context quality
universe falsifies the combined `Data Quality and Reconciliation` candidate: quality operations
evaluate purpose-scoped requirements over exact cuts, while reconciliation/control operations
compare identified populations under truth-role, matching, tolerance and materiality rules. All
37 QOR libraries have an explicit disposition; 33 selected horizontal seams map exactly into the
compiler, while data-contract, master/reference and entity-resolution meanings remain imported and
accounting/control reconciliation remains a vertical specialization. Both replacement products now
have full DDD dossiers and the four structural verticals have exact promoted remaps. The old
combined candidate has been removed. Ratification, provider qualification, portability and
executed vertical acceptance remain withheld.

`dossier_readiness/` now makes the next gap explicit across all 59 strong or presumptive products.
Every retained product has an exact boundary decision and 110-truth applicability profile, but
the five analytical-operation products, the Semantic Metric and Formula Service, BI/Reporting,
all eight movement products, four retained lakehouse products, both quality/reconciliation
replacement products, the intent-to-solution compiler, and Lineage and Provenance Evidence
and the Optimization Solver Engine currently have full product-specific 29-field DDD dossiers.
The Process and Object-Centric Mining Workbench now also has a full product-specific DDD and seven
exact, product-attributed library seams; its predictive-model and agent surfaces remain optional and
removable. The Simulation Modeling and Experiment Environment has a full DDD and six exact seams;
its stochastic methods remain typed and evidence-bound without being relabeled as AI. The
Forecasting Workbench has a full DDD and eight owned seams: four bind exactly and four lifecycle,
selection, override and publication contracts remain typed compiler gaps. The Experimentation
Platform has a full DDD and eight owned seams; five bind exactly and three integrity, analysis-binding
and conclusion-lifecycle contracts remain gaps. The Geospatial Workbench has a full DDD and thirteen
owned seams; five foundations bind exactly and eight workbench/specialized methods remain gaps.
All six model/decision products now have complete DDDs and exact decomposition: 27 product-owned
library seams plus one batch-scoring composition component. The Feature Platform and Predictive
Inference Serving retain four typed runtime gaps; the small optional model/agent extension owns
only declared tasks, bounded invocations and typed untrusted proposals and is removable. The six
query/warehouse/search/protection products now also have full DDDs and exact ownership for all sixty
seams: query/federation/cache, warehouse experience, virtual access, search/index, recovery and
preservation stay separate.
All twelve governance products now have complete DDDs. The nine formerly shallow products add 56
product-scoped seams across metadata discovery, glossary, ontology, schema, contracts,
master/reference, data-use policy, publication and marketplace. Metadata Discovery's six seams,
Business Glossary's five seams, Ontology/Knowledge Model's six seams, Schema Registry's six seams,
Data Contract Registry's seven seams, Master/Reference Data's seven seams, Data Use Policy's six,
Data Product Publication's seven and Data Marketplace's six seams now map to exact horizontal
contracts. All nine formerly shallow governance products are structurally mapped; their
implementations and provider qualification remain withheld.
All fifty-nine retained products now have complete product-specific DDDs, exact product-to-library
attribution and compiler maps. Eight are blocked by typed library/compiler gaps and fifty-one
are structurally mapped but unqualified; no internally owned required capability is left uncovered.
Managed Ingestion and Delivery now resolves its former schema-mapping gap through two exact
contracts: a cold-path, loss-explicit mapping compiler and a hot-path deterministic executor. The
split is supported by all twelve boundary lenses and preserves schema registry, ontology,
reference-data, business conversion, capture and physical-delivery ownership outside the seam.
Batch Transformation Build now resolves its two former coarse gaps through five exact contracts:
definition compiler, selection closure, incremental planner, mutation protocol and build-evidence
assembler. The compiler and selector share an editioned manifest language but differ by complete-
project versus invocation scope. Planning, target effects and evidence remain separate because
their authority, failure states, resource economics and substitution seams differ.
The platform pass adds complete DDDs for the developer platform, runtime/resource control and FinOps,
including 22 separate runtime seams and an exact FOCUS-normalization contract whose implementation
and provider qualification remain withheld. Consumption adds notebook
and embedded-analytics DDDs plus an explicit report-authoring library. Collaboration/privacy/
resolution/assurance adds four full DDDs while preserving PET, legal, source/master and relying-authority
boundaries. Only 12 products occur
in two structural vertical compositions, none has executed vertical acceptance, no provider is
qualified or portable, and no product is build-ready. The 165 generated closure work items are the
machine-readable product-by-product work queue; bundle-level proximity never counts as proof of a
product decomposition.

`qualification_program/` turns that readiness frontier into a deterministic 16-gate proof DAG for
all 59 products and 469 exact product-attributed library subjects. It keeps specification,
implementation identity, reproducible build, exact-scope execution, independent appraisal, first
qualification, second independent implementation, portability, physical binding, unrelated-
vertical generality, executed acceptance, build readiness and ratification as separate states. Its
820 evidence vacancies are open work, not synthetic failures or passes. Models, LLMs and agents may
propose typed tests, cases, counterexamples or diagnostics, but cannot approve laws, promote a gate,
authorize an effect or supply domain acceptance; removing them leaves the proof program complete.

The first mixed-vertical structural pilot is in
`composition_pilots/deterministic_verticals/`. It composes acute-care bed flow, retail tender
reconciliation, midstream pipeline nomination/capacity allocation and manufacturing finite-capacity
scheduling from industry cases through products, exact libraries and capability requirements. The
four graphs share 55 horizontal libraries while preserving different units, methods and vertical
vocabulary. No model/agent library enters any core; removal leaves all four graphs unchanged. All eight provider
substitutions fail closed and all physical bindings remain unqualified. The pipeline graph also
consumes the deterministic multi-axis model-class adjudicator: the broad problem is refused as LP,
while only a closed screening cut classifies as continuous LP. Its 23 typed transformation
relations prevent relaxations, linearizations, discretizations or simulation responses from
silently inheriting source-model claims. Provider qualification and vertical acceptance still
fail closed, so this remains a structural reuse/refusal proof rather than vertical acceptance.

## Model layers

```text
Portfolio
  -> Suite                     commercial or internal packaging
     -> Product                governed promise to a user
        -> Capability          selectable behavior offered by a product
           -> Machine          typed compositional unit
              -> Library       semantic or implementation ownership unit
                 -> Module     code/deployment unit
                    -> Provider

SolutionPack                   vertical vocabulary, rules, mappings and recipes
Standard                       interoperability contract; never silently a product
Resource                       storage/compute/network supplied through a provider contract
```

Each arrow is many-to-many unless a product-specific law narrows it. A product may compose
several capabilities and implementations; a capability may be offered by competing products.

## Files

- `PRODUCT-BOUNDARY-THEORY.md` — definitions, split/merge tests and anti-patterns.
- `truth-contract.json` — the user's 110 truth dimensions, retained as one applicability-aware
  product dossier contract rather than 110 products.
- `schema/product-graph.schema.json` — schema for nodes, relations, evidence, decisions and gaps.
- `registry/nodes.jsonl` — product-graph nodes; currently the lakehouse pilot and its dependencies.
- `registry/edges.jsonl` — typed composition and ownership relationships.
- `registry/evidence.jsonl` — source claims and limitations.
- `adjudications/lakehouse/` — deterministic evidence-backed lakehouse boundary adjudication and
  legacy-pilot crosswalk.
- `adjudications/movement/` — deterministic evidence-backed data-movement boundary adjudication,
  library contracts and global crosswalk.
- `adjudications/governance_semantics/` — evidence-backed governance and semantic ownership
  adjudication, including the glossary/ontology and schema/data-contract splits.
- `adjudications/analytical_methods/` — evidence-backed practice/method/algorithm/library/product
  adjudication with deterministic-first automation-modality laws.
- `adjudications/consumption_experiences/` — BI, embedded analytics, notebooks and presentation-
  artifact boundary adjudication.
- `adjudications/platform_control/` — compiler, developer-platform, runtime/resource and FinOps
  product boundaries plus platform-operations reclassification.
- `adjudications/model_decision_serving/` — predictive lifecycle, features, inference, assurance,
  deterministic decisioning and removable optional-extension boundaries.
- `adjudications/query_warehouse_search_protection/` — query, warehouse, virtualization, search,
  cache, recovery and preservation boundaries with exact compiler maps and negative twins.
- `adjudications/semantic_metrics_formulas/` — formula, metric, grain, aggregation, join, time,
  unit, uncertainty, semantic-query, observation and cache-equivalence product boundaries.
- `adjudications/collaboration_privacy_resolution_assurance/` — controlled collaboration,
  privacy/retention, entity-resolution and assurance-case/appraisal product boundaries.
- `adjudications/representation_codec_boundary/` — zero-product representation, codec,
  compression, loss, transcode, provider and runtime reclassification.
- `adjudications/analytical_operations/` — five operational analytical product boundaries, five
  full DDD dossiers, 60 library contracts and exact fail-closed compiler maps.
- `composition_pilots/deterministic_verticals/` — four unrelated industry-to-product-to-library
  graphs, optional-extension removal proofs and fail-closed provider substitution trials.
- `inventory_challenges/analytical_operations_gap_audit/` — evidence-backed omitted-product audit
  that originated the five now-adjudicated promotions, while retaining seven deferred hypotheses
  and its preliminary 60-library falsification surface.
- `dossier_readiness/` — derived readiness and closure-work matrix for every retained product;
  separates boundary coverage, DDD depth, library attribution, compiler maps, qualification and
  vertical acceptance.
- `qualification_program/` — the generated 16-gate product/library qualification DAG, exact
  evidence vacancies and two-unrelated-vertical acceptance slots for every retained product.
- `ANNEALING-LOG.md` — decisions, falsifiers, unresolved gaps and the next research loop.
- `validate_registry.py` — dependency-free structural, referential and truth-contract validation.

## Validation

```bash
python3 research/product_ontology/validate_registry.py
```

Passing validation establishes structural consistency only. It does not establish product-market
fit, semantic completeness, production eligibility, independent appraisal, or ratification.

## Relationship to the existing analytics corpus

This model imports research candidates from:

- `research/SAN_DATA_ANALYTICS_GPT_PRO_HANDOFF_2026-08-12/current_work/analytics_landscape/`
- the 21-context data-platform DDD model;
- the 53-machine/16-library composition seed; and
- the external prose describing 99 candidate DAT semantic libraries.

It does not equate any of those counts with products. The unavailable machine-readable 99-library
archive remains unverified evidence, not a registry input that can be silently trusted.
