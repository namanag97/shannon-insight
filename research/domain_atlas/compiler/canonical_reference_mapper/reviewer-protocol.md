# Canonical-reference reviewer protocol

## Reviewer contract

Review the source concept and target contract, not the spelling. The mapper's authoring review is not
independent review. A reviewer must have appropriate domain competence and must not treat the current
`proposed` state as an adjudication shortcut.

For each batch member:

1. Open the queue item and its `source_definition_ref`.
2. Inspect every materially distinct source occurrence, especially different packs, decisions,
   populations, grains, jurisdictions, time models and evidence regimes.
3. Open every candidate target in `canonical-candidate-index.jsonl`; compare definition, owner layer,
   assumptions, input/output contract, laws, uncertainty, failure/refusal states and evidence.
4. State the relation in the source-to-target direction: `equivalent`, `narrower`, `broader`,
   `overlap`, `disjoint`, or `missing_canonical_concept`.
5. Check cardinality. Preserve alternatives and one-to-many decomposition. Do not collapse a compound
   method, source surface or cross-activity industry scope merely to simplify compilation.
6. Enumerate information loss. Vertical actors, decision authority, policy, grain, thresholds,
   jurisdiction, evidence and failure modes normally remain outside a broader horizontal target.
7. Record uncertainty and defeaters. A candidate target's own hypothesis status limits confidence.
8. Check `collisions-homonyms.jsonl` and `negative-tests.jsonl` before accepting a same-label mapping.
9. If no target preserves the meaning, keep the queue item open and refine its missing-concept
   proposal. A gap is preferable to a false mapping.
10. Submit the review to the separate adjudication workflow. Do not change these generated records by
    hand; update reviewed authoring seeds and regenerate only after governance approval.

## Relation tests

```text
equivalent  source and target have the same extension and compatible laws/evidence
narrower    every lawful source instance is a target instance; target admits more
broader     every target instance is a source instance; source admits more
overlap     some instances/obligations intersect, but neither contains the other
disjoint    definitions or laws rule out intersection
missing     no registered target preserves the required concept boundary
```

Equivalence requires more than equal labels or an official code table. Check statistical unit,
concept, geography, time, inclusion/exclusion, missingness, uncertainty, authority and failure
semantics. Cross-edition and cross-axis classification equivalence requires an evidence-bearing
crosswalk. A provider type is not an economic activity; a source is not a shape; a method is not a
KPI; simulation is not optimization; and an untyped verb is not a typed operation.

## Confidence

- `high` — the proposed direction/decomposition is directly supported by source context and target
  contracts, with narrow residual uncertainty.
- `medium` — the family relation is reviewable, but specialization, layer or some source contexts
  remain open.
- `low` — a partial overlap is useful for review, but important law, estimand, authority or lifecycle
  dimensions are absent.

Confidence never changes status to adjudicated.

## Required review lanes

The generated batches partition the queue once by primary pack, domain and lane. Multi-pack references
must still be checked against every occurrence. Finance reviewers must explicitly inspect CCR
occurrences (`banking.ccr`) because the same broad method references also occur outside CCR. Healthcare,
manufacturing, logistics, energy, public, commerce, telecom/media/tech and built/food/environment each
require a domain reviewer. Lossy, one-to-many, cross-axis, cross-edition, low-confidence and
missing-concept records require an additional classification or semantic-owner reviewer.

## Refusal conditions

Refuse or return a proposal to open triage when:

- evidence establishes only a shared label or vendor claim;
- the source's case-specific obligation would be erased;
- an operation lacks typed inputs, outputs, failure or partiality semantics;
- a source phrase combines distinct authority or interface surfaces but the proposal picks one;
- an industry mapping changes edition, statistical unit or classification axis silently;
- an apparent alias is not declared by the canonical record or official crosswalk;
- an LLM/generative concept is being smuggled into the non-generative core through a lexical twin;
- the relation direction is unclear; or
- a missing canonical concept would be hidden by a convenient broader family.
