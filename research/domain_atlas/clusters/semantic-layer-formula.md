# Semantic layer and formula cluster — boundary candidate

## Why this is not one bounded context

```text
Business ontology
      |
      v
Analytical entities + facts + measures + dimensions
      |
      +-----------> Relationship / valid-join graph
      |                         |
      v                         v
Metric definition -------> Semantic model publication
      ^                         |
      |                         v
Formula binding <--------- Semantic query
      ^                         |
      |                         v
Pure formula algebra      Semantic lowering
      |                         |
      v                         v
Formula evaluation        Logical/physical query products
      \_________________________/
                    |
                    v
             Metric observation
```

The terms below are false twins:

```text
measure            != metric
metric definition  != metric observation
formula expression != registered formula definition
formula binding    != formula evaluation
semantic query     != physical query plan
relationship       != valid join path
grain              != database primary key
time dimension     != valid time or snapshot cut
aggregation        != statistical estimator
null               != unknown != missing != suppressed != not-applicable
```

## Candidate bounded contexts

| Candidate | Sovereign question |
|---|---|
| Analytical Entity | What real/domain concept plays an analytical entity role? |
| Grain | What does one observation/fact row represent, including uniqueness and cardinality? |
| Fact and Measure | What phenomenon is measured, in which unit and with what aggregation posture? |
| Dimension and Hierarchy | Along which governed attributes and levels may observations be grouped? |
| Relationship and Join Path | Which semantic relationships permit which joins under what cardinality? |
| Pure Formula Algebra | What typed expression means, independent of registry, I/O or provider? |
| Formula Registry | Which named formula edition is current, compatible, deprecated or recalled? |
| Formula Binding | How do variables/functions bind to owned measures, metrics, parameters and time? |
| Formula Evaluation | How is a bound expression evaluated with budgets and retained receipts? |
| Metric Definition | What measure over what population, grain, filters, dimensions and time is meant? |
| Metric Policy | Which metric edition is authoritative for a purpose and who may publish/change it? |
| Semantic Model | Which entities, datasets, relationships, measures, dimensions and metrics compose? |
| Semantic Publication | Which semantic-model edition is published to which consumers? |
| Semantic Query | What governed analytical result is requested without selecting a physical engine? |
| Semantic Lowering | Can the semantic request be lowered to target capabilities without meaning loss? |
| Metric Observation | What result was observed for an exact semantic edition and data cut? |

## Invariants spanning the cluster

1. Every term and semantic reference resolves to exactly one owner and positive edition.
2. Every metric declares population, grain, measure, filters, aggregation, dimensions and time.
3. Every formula variable and function has an exact typed binding and absence semantics.
4. Units and dimensions are checked before execution; conversions are explicit and evidenced.
5. Cycles are refused unless a declared fixed-point algebra and convergence/budget law applies.
6. Join paths declare cardinality and fanout behavior; ambiguous paths are refused.
7. Non-additive and semi-additive measures cannot be aggregated outside declared dimensions/time.
8. Formula registry authority does not grant data access or metric-publication authority.
9. Semantic lowering preserves result semantics or emits an unsupported/loss refusal.
10. A metric observation pins formula, metric, semantic-model, policy and exact data-cut editions.
11. Cache/materialization reuse requires semantic and cut equivalence, not matching display names.
12. Corrections and recalls do not silently overwrite historical observations.

## Open registries governed by this cluster

The following are configuration/definition records, not one bounded context per entry:

- arithmetic, comparison, logical, temporal and collection operators;
- statistical and financial functions;
- enterprise formulas;
- metric definitions;
- calendars and time-intelligence policies;
- unit conversions;
- semantic-model definitions;
- backend lowering/provider capability profiles.

## Evidence anchors

- Apache Ossie candidate schema: portable datasets, relationships and metrics.
- SDMX information model: dimensions, attributes, measures and data-structure definitions.
- OASIS OpenFormula: explicit formula data types, syntax, functions and semantics.
- OGC Observations, Measurements and Samples: feature, property, procedure, sample and result.

These are evidence and interoperability targets. None becomes the universal semantic owner merely
because it is standardized.

