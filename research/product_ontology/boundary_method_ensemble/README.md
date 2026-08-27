# Boundary-method ensemble

No single modeling method can derive the complete SAN ontology.

```text
strategy/value       Wardley, capability/value-stream maps, JTBD, product discovery
domain meaning       DDD, EventStorming, Domain Storytelling, terminology work
work behavior        BPMN, CMMN, DMN, statecharts, Petri nets, process mining
information          conceptual/ER/fact models, ontology, SHACL, dimensions, contracts
software structure   C4, arc42, ports/adapters, coupling, EDA, Team Topologies
reuse/variability    FODA, software product lines, decision and feature models
formal correctness   Alloy, TLA+, contracts, property/model tests, theorem proving
system/trust         SysML, STPA, threat/privacy modeling, FMEA/fault trees
operation/economics  SRE, resilience, capacity, FinOps
empirical challenge  field research, literature review, code/log/usage mining, red teams
analytics            measurement, statistics, causal models, OR, simulation
```

Each method is useful only for the question it was built to answer. Its output is evidence for a
particular boundary axis, never an automatic product, context, library or compiler record.

The compiler corpus therefore requires twelve independent lenses. A product/context/library seam
remains `UNDETERMINED_NOT_PASS` when an applicable lens has not been evaluated. Agreement across
methods raises confidence; disagreement is retained as a typed hotspot and drives another research
or falsification loop.

The generated `methods.jsonl` currently records more than seventy named methods across eleven
families, including each method's primary question, outputs, useful seam evidence and explicit
non-claim. This is an open-world method registry, not a claim that no other useful method exists.

## Application rule

```text
candidate seam
  -> select every applicable method family
  -> produce method-native evidence
  -> normalize claims without erasing their scope
  -> compare support, counterpressure and missing evidence
  -> adjudicate the boundary kind
  -> encode residual uncertainty
  -> falsify with unrelated cases and implementations
```

The first triangulation revises Metadata Discovery to one product, three bounded contexts and six
libraries. That result is stronger than the earlier one-library/one-context mechanical split, but
it remains a candidate until domain experts, implementations and executed operational evidence
challenge it.
