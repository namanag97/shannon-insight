# Semantic metrics and formulas universe

This directory is an open-world, provider-neutral research corpus for the **meaning layer**. It
models facts, observations, dimensions, measures, metrics, formulas, joins, populations,
aggregation, units, time, uncertainty, semantic query, evaluation, materialization, cache reuse
and disclosure. Every record is a candidate until its owner, laws and provider evidence are
independently adjudicated. The corpus makes no completeness claim.

Analytical cases and method selection belong elsewhere. Physical query algorithms and kernels
belong to `query_compute_kernels`. Dashboards, reports and visual encodings belong to
`consumption_bi_visualization`. LLM/generative semantics are explicitly excluded.

## Horizontal context map

```text
owned domain language                          observational projection
business concept -------------------------> analytical entity role
        |                                  / fact / event / observation
        |                                 /            |
        |                                v             v
        +-------------------------- dimension       grain + population
                                       |              |
                               member + hierarchy     measure + unit
                                       \              /
                                        v            v
entity relation -----------------> valid join path -> fanout proof
                                                     |
pure formula algebra                                  |
AST -> semantic types -> operators/functions          |
 |           |                  |                     |
 |     missingness      units/currency/ratio          |
 v           v                  v                     v
formula definition -> binding -> evaluation <- metric definition
                                             /   |     \
                              filter/cohort -+  time   KPI/target/benchmark
                                                 |
                                    valid + recording + as-of/finality
                                                 |
semantic model -> publication -> semantic query -> validation -> lowering
                                                               |
                                   materialization <- evaluation -> observation
                                          |                         |
                                          v                         v
                               semantic-equivalence cache       disclosure
                                          \                         /
                                           purpose-bound access

Across every arrow: identity + edition + authority + proof/refusal + evidence.
```

The 52 contexts are intentionally finer than a single “semantic layer.” Their 64 candidate
relationships are in `context-relations.jsonl`; split/merge decisions remain open.

## Identities that must remain separate

```text
business term        != dimension member
observation          != fact
event                != snapshot
measure              != metric != KPI
metric definition    != metric observation
formula expression   != formula definition
formula definition   != binding != evaluation
variable             != caller parameter
null                 != absent != unknown != suppressed != not-applicable != zero
empty population     != all values missing
entity relation      != authorized analytical join
join cardinality     != row-count estimate
additivity           != decomposability
aggregate result     != sufficient merge state
target               != benchmark != observed value
unit conversion      != currency valuation
event time           != valid time != recording time != query time
freshness            != finality
semantic query       != SQL text
semantic cache reuse != matching SQL text
governed metric      != dashboard tile
```

## Formula contract

Formula syntax is a typed AST. A formula definition gives an AST registry identity and immutable
edition. A binding resolves every free variable, measure, metric, dimension and function to one
owner and edition. Evaluation consumes a bound formula, explicit inputs, a bitemporal data cut,
budgets and allowed effects, then returns a value-or-error plus a receipt.

```text
FormulaDefinition = identity × edition × TypedAST × dependency contract × lifecycle
FormulaBinding    = definition × exact semantic references × type/unit/grain/time proofs
Evaluation        = binding × inputs × cut × effect budget × provider -> value | error + receipt
```

Pure expressions have no ambient clock, data access, registry lookup, randomness or I/O. A
function that reads semantic data, uses window state or samples a distribution declares that
effect. Partial functions state their domain and their absence/error result. Recursive cycles are
refused unless a fixed-point algebra, monotonicity/convergence law and finite budget are declared.

## Aggregation, fanout and cache laws

An aggregation record declares input collection semantics, null/absence treatment, empty-input
result, order/tie policy, exactness, sufficient state and merge law. Additivity answers where a
value may be summed. Decomposability answers whether a sufficient state may be partitioned and
merged. They are independent properties.

For every selected measure, a fanout-safe join must prove that source contribution multiplicity is
preserved. A many-to-many relation needs allocation weights, preaggregation at a compatible grain,
stable-key deduplication that fits the measure, or refusal. Relationship existence never supplies
that proof, and ambiguous paths are never selected silently.

A semantic cache key covers the normalized semantic AST/query, every referenced edition,
population, grain, filters, grouping, time/calendar/zone, missingness, units/valuation,
uncertainty/exactness, data cut, access projection and disclosure posture. Matching SQL text is
neither necessary nor sufficient. A covering materialization also needs a containment and legal
reaggregation proof.

## Time and observations

Bitemporal interpretation selects valid time and recording time independently. Event time and
query time remain separate roles. Calendar/fiscal bucketing pins calendar, time zone database,
boundary and period editions. Corrections append or supersede; they never rewrite prior metric
observations. Freshness, completeness, validity and finality are separate disclosure coordinates.

Every observation receipt pins the metric, formula, binding, semantic model, policy, provider,
data cut, calendar/rate editions, value-or-error, uncertainty and supersession status.

## Worked verticals without engine branches

`vertical-examples.jsonl` applies the same generic contracts to two unrelated domains:

- Counterparty credit exposure evaluates a per-netting-set formula after fanout-safe collateral
  aggregation and explicit currency valuation. Counterparty limits remain separate targets.
- Hospital staffed-bed occupancy evaluates a ratio of reaggregated counts at a bitemporal census
  cut. A zero denominator yields an explicit undefined result, and facility percentages are never
  averaged.

Neither example changes the compiler or introduces an industry switch; each is only a different
set of semantic definitions and bindings.

## Generated artifacts and exact counts

| Artifact | Records |
|---|---:|
| `bounded-context-candidates.jsonl` | 52 |
| `context-relations.jsonl` | 64 |
| `semantic-records.jsonl` | 400 |
| `ubiquitous-language.jsonl` | 86 |
| `invariants-refusals.jsonl` | 69 |
| `lifecycles.jsonl` | 12 |
| `compiler-mappings.jsonl` | 36 |
| `library-boundaries.jsonl` | 24 |
| `sources.jsonl` | 91 |
| `evidence.jsonl` | 91 |
| `innovations-2021-2026.jsonl` | 26 |
| `vertical-examples.jsonl` | 2 |
| `gaps.jsonl` | 24 |

The 400 semantic records comprise 42 semantic types, 26 AST nodes, 21 formula operators, 53
formula functions, 30 aggregations, 22 join laws, 26 time semantics, 132 operations and 48 decision
points. Ninety of
the 91 source records are classified as primary or official evidence; the remaining community
specification is labeled as such. Thirteen JSON Schemas cover every JSONL record family.

## Deterministic build and validation

```bash
python3 research/domain_atlas/universes/semantic_metrics_formulas/build_corpus.py
python3 research/domain_atlas/universes/semantic_metrics_formulas/validate_corpus.py
```

The validator compares every generated record and schema with the builder's in-memory canonical
form; validates IDs, required fields and references; enforces minimum category coverage; checks the
named false-twin distinctions, proof-law families, pure/effectful boundary split, recent-innovation
window and branch-free vertical examples; and reconciles manifest/report counts.

## Evidence and honest gaps

The evidence index includes OpenFormula/ODF, SDMX, RDF Data Cube, DCAT, PROV, OWL-Time, SHACL,
SPARQL, QUDT, UCUM, ISO/NIST quantity and time sources, JCGM uncertainty guidance, OGC observation
standards, SQL/OLAP specifications, open semantic-model/query implementations and foundational
research. Evidence is scoped: a first-party implementation document does not establish universal
semantics or cross-provider conformance.

Known gaps are first-class records. They include portable formula binding, temporal hierarchy
summarizability, data-dependent cardinality, holistic fanout safety, semantic cache containment,
uncertainty interchange, fiscal-calendar exchange, bitemporal metric support, recall propagation,
access-equivalent cache proof, approximate error composition and independent vertical review.
