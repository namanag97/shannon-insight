# Analytical method and product-boundary adjudication

Status: evidence-backed adjudicated candidate, not ratified products or qualified providers.

The constitutional separation is:

```text
business question / decision need
        |
        v
analytical practice and study design
        |
        v
formal method / estimand / model
        |
        v
algorithm + pure/effect-bounded library
        |
        v
governed execution environment or workbench
        |
        v
independently adopted product
        |
        v
reviewed decision handoff -> separate effect authority
```

This slice retains six horizontal product candidates: experimentation platform,
forecasting workbench, optimization solver, process-mining workbench, geospatial
workbench, and simulation environment. Statistics, causal inference, anomaly/change,
graph, text/document, and media/signal remain semantic method and library families
unless a distinct job-specific product promise is separately proven.

The 58 records in `library-contracts.jsonl` are product-facing contract groups plus exact
optimization, process-mining, simulation, forecasting and experimentation product libraries, not
provider selectors. `product-library-binding-maps.jsonl` projects each group onto the
concrete compiler library and requirement registries. A group is directly unusable when
`product-library-binding-gaps.jsonl` names a missing or insufficiently cohesive concrete
contract.

```text
product requirement
      -> abstract analytical contract group
      -> one or more concrete library requirements
      -> qualified provider/target offers
      -> binding + rejected alternatives + receipts

media/signal group
      +-> sampled-signal methods
      +-> image/vision methods
      `-> explicit composition when both are required

text group
      +-> Unicode/text semantics
      +-> indexing/query/ranking
      +-> document containers/parsers/content graphs
      +-> layout/OCR/table/form extraction
      `-> classification/information extraction + evaluation
```

This edition reports zero exact compiler-library gaps. All 58
product-facing libraries/groups lower to exact library requirements; this
does **not** mean that a provider, target or vertical solution has qualified. A source package or
product name cannot fill those later proof obligations.

The Process and Object-Centric Mining Workbench now has a complete 29-field DDD and seven exact
product-owned libraries: event/object projection, case projection, State-Aware OCEL derivation,
temporal-EKG projection, discovery, conformance and performance analysis. OCED core, OCEL 2.0,
serialization and provider occurrence remain different identities; a generated state event is not
a source event; a case projection is a lossy view; a discovered model is not process truth; and a
deviation or bottleneck association is not a defect, root cause or intervention authority. Generic
artifact envelopes, result algebra and provider qualification are imported instead of being
absorbed into the product. Predictors, GNNs, LLMs and agents are optional proposal mechanisms;
removing all of them preserves the deterministic process-mining core. No provider has yet earned a
qualified or portable binding.

Statistics, causal inference, the four forecasting method kernels and anomaly/change are
structurally closed over exact contributions and qualification profiles. Their former broad library records remain
compatibility facades and are forbidden from exact product bindings. Structural closure does not
qualify SciPy, statsmodels, R, Stan, PyMC, DoWhy, DoubleML, EconML, sktime, StatsForecast,
scikit-learn or River.

The Forecasting Workbench and Service now has a complete 29-field DDD and eight exact
product-owned seams. Time-series/information-cut semantics, estimator execution, rolling-origin
evaluation and hierarchy reconciliation map to existing compiler libraries. The four former gaps
now map to eight contracts: selection-profile compilation and evidence appraisal; forecast
definition compilation and edition/run/artifact lifecycle; override-policy compilation, lifecycle
and ex-post value evaluation; and a forecast publication-profile compiler. Selection appraisal
imports generic authority adjudication, while the publication profile composes the shared
data-product publication, consumer-change and recall protocols instead of duplicating them.
Classical statistical, ML, deep and foundation forecasters obey the same estimator, leakage,
uncertainty and qualification contracts. Models and agents can propose candidates or overrides but
cannot select, approve, publish or manufacture evidence.

Graph and the five foundational geospatial method bindings are structurally closed over exact contracts. Graph
representation/view semantics, traversal/path algorithms, centrality, community/partition and
GraphBLAS/semiring kernels are distinct. Spatial CRS/support semantics, coordinate transformation,
vector topology, raster/grid methods and spatial statistics are also distinct. The former broad
`graph_methods` and `spatial_methods` records are compatibility facades and cannot satisfy exact
bindings. NetworkX, igraph, LAGraph, SuiteSparse:GraphBLAS, GEOS, PROJ, GDAL, PostGIS and PySAL
remain observed, unqualified offers.

The Geospatial Analysis Workbench now has a complete 29-field DDD and thirteen product-owned
seams. Spatial-reference/support semantics, coordinate transformation, vector topology, raster
grids and spatial statistics bind exactly. The eight former specialized gaps lower to eighteen
contracts: project definition and layer lifecycle; workflow definition, execution planning and run
evidence; geocode profile, gazetteer resolution and accuracy evaluation; network profile and
route/accessibility evaluation; trajectory construction and mobility evaluation; terrain profile
and hydrology evaluation; point-cloud profile and 3D evaluation; spatial-result accuracy appraisal
and publication-profile compilation. Generic storage/query, graph kernels, provenance,
adjudication, publication, consumer-change and recall remain imported. Source
feature/place/legal-boundary truth, cartographic UI, optimization/dispatch and operational effects
remain outside. Learned methods and agents may propose candidates, but cannot invent a CRS,
identity, topology, accuracy, disclosure decision or authority.

The exact experimentation method/state core separates prospective protocol/eligibility,
assignment state, randomization/allocation, actual exposure occurrence, immutable analysis
cuts/stopping, inferential tests and causal effect estimation. Assignment is not exposure, an
exposure is not a metric observation, and no feature-flag provider is the whole experiment.
GrowthBook and Statsig are observed unqualified offers only.

The Experimentation Control and Analysis Platform now has a complete 29-field DDD and eight
product-owned seams. Protocol semantics, assignment state, randomization, actual exposure and
analysis-cut/stopping map exactly. Three former coarse gaps now lower to six contracts: prospective
integrity-profile compilation; observed integrity evaluation; sealed protocol/cut-to-estimator
analysis binding; immutable result sealing; evidence-bounded conclusion appraisal; and conclusion
publication, correction, retraction, supersession and decision-evidence handoff.
Generic analysis design, inferential tests and causal estimators are imported methods; feature or
treatment delivery, consent/ethics/safety decisions, and release activation remain external
authorities. Findings do not stop experiments; execution success does not validate results;
estimates are not conclusions; publication is not truth; and retraction issuance is not propagation
completion. Agents can propose hypotheses or plans, but cannot seal protocols or evidence, infer
exposure, approve stopping, strengthen or publish conclusions, or release treatments.

Optimization and simulation now bind through the dedicated operations-research universe rather
than a generic bridge. The Optimization Solver Engine now has a complete 29-field product DDD and
nine exact product-attributed libraries. Its boundary deliberately excludes business decision
framing while retaining declared objective/constraint algebra, model IR, solver capability,
bounded execution, result algebra, independent validation, infeasibility diagnosis and governed
heuristic semantics. Simulation separates model semantics, experiment design,
random streams, execution, output analysis and verification/validation. OR-Tools, HiGHS, SCIP,
Gurobi, AnyLogic and Simio are observed unqualified offers; no run, proof or reality-fit claim is
inferred from a provider name.

The Simulation Modeling and Experiment Environment now also has a complete 29-field DDD and six
exact product libraries for those simulation seams. It treats discrete-event, agent-based,
continuous, system-dynamics, Monte-Carlo and hybrid simulation as declared method paradigms—not as
an ambient AI category. Scenario is not forecast; seed is not stream allocation or independence
proof; run completion is not a valid estimate; verification is not validation; calibration is not
truth; and simulated comparison is not a real-world causal effect, optimized decision or
authorized action. Optional learned components, LLMs and agents can be removed without weakening
the deterministic/stochastic experiment path.

Deterministic document analysis is structurally closed without treating “text analytics” as one
algorithm. Container/profile semantics, a positioned content graph, parser adapters, layout, OCR,
tables, forms, provenance/loss, classification, information extraction and extraction evaluation
are independent contracts. Apache Tika, PDFBox, Tesseract, Table Transformer, spaCy and OpenNLP
remain observed, unqualified offers.

Models, LLMs and agents are supported as optional typed modalities. They can propose
code, configuration, hypotheses, explanations or tool calls. They cannot acquire
method semantics, validate their own evidence, approve conclusions, or execute a
business effect. If removed, a deterministic core remains or the compiler emits an
explicit unavailable-capability gap.

The optional extension now exposes provider-neutral requirement and qualification records rather
than merely naming model/agent libraries. Every requirement is optional or intent-required, uses an
`omit_optional` fallback, and is forbidden from satisfying a deterministic core requirement.
Provider adapters remain declared, unqualified offers with empty conformance receipts.

Agent availability is not evidence that the hard work occurred. Parsing, typechecking,
constraint solving, numerical execution, provider qualification, authorization and receipt
verification remain explicit deterministic compiler obligations. An agent may request or assist
those mechanisms, but its proposal is neither their result nor their proof.

`source.json` is canonical. Run `python3 optimization_enrichment.py`,
`python3 build_bundle.py` and `python3 validate.py`.
