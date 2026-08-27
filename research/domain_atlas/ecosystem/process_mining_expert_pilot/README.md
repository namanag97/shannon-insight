# Process-mining expert portfolio falsification pilot

This bundle demonstrates how an expert census must become a compiler-usable contribution graph. It does **not** say “Dirk Fahland = process mining” and attach a list of titles. It separates people, bibliographic artifacts, formal contributions, implementations, datasets, canonical mappings, and library boundaries. The pilot is deliberately bounded to Dirk Fahland's portfolio and the adjacent experts required to identify object-centric/event-graph contributions correctly.

The generated manifest currently reports the authoritative counts. Run the build and validator rather than copying counts into downstream documents.

## Why this pilot exists

The user's examples are a useful negative test:

```text
raw remembered term
       |
       v
identity/adjudication queue
       |
       +-- HOEG  ----> Heterogeneous Object Event Graph encoding
       |               Smit / Reijers / Lu; NOT Fahland
       |               representation + GNN predictor (predictor excluded from non-AI core)
       |
       +-- TEKGM ----> unresolved spelling
       |               candidates: EKG or process-mining tEKG; no automatic alias
       |
       +-- tEKG  ----> Temporal Event Knowledge Graph
       |               Khayatbashi / Hartig / Jalali
       |               OCEL 2.0 -> snapshot-bearing property graph
       |               distinct from TEILP's separate TEKG usage
       |
       +-- SA-OCEL --> State-Aware OCEL, Definition 2 of SA-OCPM
       |               Kretzschmann / Berti / van der Aalst
       |               derived log model; NOT an OCEL standard edition
       |
       +-- OCED  ----> community core model + design space
                       Fahland et al.; distinct from OCED-PG and OCEL 2.0
```

An attribution mismatch is not clerical noise. It proves a constitutional rule for the global registry:

```text
person != paper != contribution != method != representation
       != algorithm != fitted model != tool != dataset != standard

authorship != supervision != maintenance != implementation
           != working-group leadership != conceptual influence
```

## Decomposition

```text
SOURCE / DOMAIN RECORDS
  source tables, ERP records, logs, XES, OCEL 2.0
                    |
                    v
EVENT-DATA PREPARATION
  extraction -> identity/correlation -> activity abstraction -> quality/provenance
                    |
         +----------+------------------+
         |                             |
         v                             v
CASE-CENTRIC                     OBJECT-CENTRIC / GRAPH
  trace + case                    OCED core concepts
  XES                             OCEL 2.0 exchange
                                  EKG property graph
                                  tEKG snapshots/history
                                  State-Aware OCEL state events
         |                             |
         +-------------+---------------+
                       v
BEHAVIORAL CONSTRUCTION
  process execution / case projection / variant
  directly-follows / entity-qualified directly-follows
  process tree / Petri net / OCPN / OPID / proclet
                       |
       +---------------+----------------+----------------+
       |               |                |                |
       v               v                v                v
  DISCOVERY       CONFORMANCE       DIAGNOSTICS      PERFORMANCE
  IM / OCPN       alignments        anomaly dims     spectrum
  proclets        SMT/identity      task patterns    batching
  graph DFG       deviations        root-cause       queues/resources
                                     hypotheses       dynamic bottlenecks
                       |
                       v
EVIDENCE AND DECISION SUPPORT
  witness graph / alignment / metric / pattern / limitation / provenance
  never silently upgrade association, anomaly, or predecessor into cause
```

The corpus keeps these non-collapsible chains explicit:

```text
OCED abstract core
  != OCEL 2.0 conceptual model
  != JSON/XML/SQLite serialization
  != OCED-PG base ontology
  != domain reference ontology
  != semantic-header mapping contract
  != PromG/Neo4j execution occurrence

EKG
  -> optional OCEL-to-EKG transformation
  -> tEKG adds entity snapshots and temporal succession

OCEL 2.0
  -> State-Aware OCEL adds generated state-change events and state context
  -> Coalesced State-Aware OCEL is another explicit representation choice

event evidence -> diagnostic observation -> candidate explanation
               != adjudicated cause -> intervention -> measured effect
```

## Machine-readable files

- `sources.jsonl`: primary papers, official specifications, repositories, datasets, and authoritative records.
- `experts.jsonl`: people and only their explicitly linked contribution records.
- `contributions.jsonl`: paper-level and sub-artifact contributions with formal objects, operators, algorithms, guarantees, assumptions, partiality, lifecycle, I/O, runtime posture, evidence, limitations, context, and decisions.
- `canonical-mappings.jsonl`: candidate practice/method/operation/representation/kernel/library/compiler mappings. They intentionally require global adjudication.
- `library-boundaries.jsonl`: proposed pure/runtime/adapter/test seams and exposed decisions.
- `review-queue.jsonl`: acronym, identity, attribution, and status resolutions or quarantines.
- `coverage-gaps.json`: limitations and non-collapsible laws.
- `schemas/`: JSON Schema Draft 2020-12 contracts for every JSONL record family.
- `build_corpus.py`: deterministic generator.
- `validate.py`: independent schema, reference, coverage, negative-twin, non-AI-core, count, and content-digest validator.

## Compiler/library interpretation

For every contribution, compilation should follow a typed chain rather than selecting a paper or expert name:

```text
declared analytical intent
  -> required semantic question and evidence kind
  -> required event/object/time representation
  -> admissible preparation/correlation/abstraction decisions
  -> method with applicability assumptions
  -> algorithm with conditional guarantees
  -> kernel/runtime with resource and partial-result contract
  -> adapter/provider occurrence with exact version qualification
  -> result + witness + provenance + residual/information-loss record
```

The generated library candidates use four boundaries:

```text
pure     semantic types, laws, total/partial operators; no I/O
runtime  executable algorithm, resource envelope, cancellation/failure
adapter  OCEL/XES/JSON/XML/SQLite/Neo4j/ProM/PM4Py/tool boundary
test     law oracle, conformance fixtures, negative/adversarial twins
```

These are candidates, not automatic one-crate-per-paper recommendations. Global library adjudication must deduplicate shared semantic types and decide whether a contribution is a method, operator, representation, kernel, adapter, test oracle, or research-only reference.

## Key limitations

- This is a deep falsification pilot, not a complete review of every one of Fahland's listed publications and not a global process-mining expert census.
- Complete paper bylines are encoded for the identity-critical acronym examples; other records retain linked portfolio authors and defer the authoritative full byline to the primary source.
- Empirical results do not establish cross-industry or cross-runtime qualification.
- HOEG's predictor is excluded from the non-AI core. The encoding remains a non-core reference because its evidence comes from the predictive/GNN study.
- `TEKGM` remains unresolved. The registry must not invent aliases.
- A valid OCEL/XES/graph artifact may still be semantically wrong, incomplete, biased, or unfit for the analytical question.

## Build and verify

```bash
python3 research/domain_atlas/ecosystem/process_mining_expert_pilot/build_corpus.py
UV_CACHE_DIR=/tmp/shannon-uv-cache uv run --offline --with jsonschema \
  python research/domain_atlas/ecosystem/process_mining_expert_pilot/validate.py
```

The validator deliberately checks the HOEG misattribution as a negative twin. If Dirk Fahland is ever attached to HOEG as an author in this corpus, validation fails.
