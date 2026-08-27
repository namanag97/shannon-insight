# P2 public-symbol owner adjudication

P2 converts the completed P1 research corpus into a lossless owner-decision surface. It does not
select an owner, import, qualified homonym, rename, merge or rejection automatically and it does not
modify canonical registries.

The scope is all 210 repeated public-symbol packets and all 666 exact declaring-library
occurrences. This corrects an easy counting mistake: 191 packets remain in the P1 archetype batches,
but the 19 directly researched high-fanout packets also remain owner-unratified. Research completion
removed those 19 from the residual research queue; it did not ratify their ownership.

## Artifacts

- `disposition-ontology.json` defines symbol-level dispositions, occurrence relations, required
  ratification fields and non-collapse laws.
- `owner-adjudication-dockets.jsonl` contains one decision-ready but unratified docket per symbol.
  Every docket binds its P1 packet, research basis, sources, candidate roles, candidate disposition
  and owner hypotheses, required decisions, non-collapse laws, exact occurrence count and authority
  limits.
- `occurrence-disposition-candidates.jsonl` contains one row per exact symbol occurrence. Every row
  preserves the current library, public name and definition digest and requires an explicit
  `OWNER_DECLARATION`, exact/profiled import, qualified homonym, rename/migration, retirement,
  rejection or unresolved result.
- `owner-decision-units.jsonl` forms a reversible quotient: 19 direct high-fanout dockets plus 89
  residual research batches yield 108 coordination units. Coordination never changes the decision
  grain, which remains one decision per symbol and per occurrence.
- `owner-decision-waves.jsonl` schedules cross-family candidates first, family owners and homonym
  conflicts next, and exact occurrence dispositions only after the relevant symbol owners are
  ratified.
- `owner-proposals.jsonl` ranks only the libraries that actually declare each repeated symbol. The
  ranking uses library class, explicit P1 hypotheses and declared semantic-contract dependencies as
  evidence; name overlap is weak support only. Provider adapters and target backends cannot be
  proposed as semantic owners. A candidate survives only if removing all name-derived score
  features preserves the same owner set. The current corpus names candidates for 116 symbols and
  blocks 94.
- `occurrence-relation-proposals.jsonl` projects a proposed owner decision onto all 666 exact
  occurrences without changing them. It proposes 321 relations and leaves 345 unresolved.
- `proposal-conflicts.jsonl` preserves 118 open conflicts, including proposals where some local
  contexts have a plausible owner but the complete multi-context owner map is still incomplete.
- `owner-proposal-counterfactuals.jsonl` executes the name-removal test for all 210 dockets. It
  records 195 stable results and 15 unstable results; instability blocks the final proposal even
  when the original scoring named an owner.
- `challenge-ontology.json` defines five orthogonal review causes: counterfactual instability,
  incomplete context-owner map, unresolved symbol disposition, rejected implementation locus and
  insufficient owner separation.
- `owner-adjudication-challenge-packages.jsonl` factors all 118 open conflicts losslessly into 29
  reusable review packages by challenge cause, P1 research route and semantic archetype. Evidence
  and counterexamples may be shared inside a package; owner and occurrence decisions may not.
- `ratification-contract.json` defines the exact receipt payload, refusals and non-claims for an
  authority decision.
- `owner-ratification-packet-templates.jsonl` binds every docket, proposal, counterfactual and exact
  occurrence relation to the input snapshot. Ninety-two templates are ready to be presented to a
  named authority; 118 remain blocked by their challenge package. Every submission field and receipt
  remains empty.
- `summary.json` binds the output to a content-addressed P1 input snapshot.

## Four decision waves

```text
Wave 1: cross-family shared-owner candidates (38 symbols)
        |
        +-----------------------------+
        v                             v
Wave 2: family owner/imports      Wave 3: homonym/conflict splits
        (95 symbols)                      (77 symbols)
        +-----------------------------+
                      |
                      v
Wave 4: 666 exact occurrence dispositions
```

The waves are a dependency order, not a bulk approval mechanism. A decision unit may share evidence
and counterexample review, but no member inherits an owner, equality relation or occurrence
disposition from another member.

## Ratification gate

A symbol cannot leave `UNRESOLVED` until a named authority supplies a content-addressed receipt that
binds the exact input snapshot and records the chosen disposition, semantic owner or complete local
owner map, definition/equality/lifecycle contract, public name, occurrence decisions, migration
plan, effective edition, approval time and signature or attestation reference.

An occurrence cannot be changed until the symbol-level owner decision is ratified. A ratified owner
decision still does not prove an exact schema, implementation, conformance, portability, product
acceptance or vertical fitness.

Rebuild and validate:

```text
python3 build_p2.py
python3 validate.py
```

The deterministic checkpoint contains 210 unresolved dockets, 666 unresolved canonical occurrence
decisions, 108 owner-decision units and four waves. It also contains 116 counterfactually stable
named owner proposals, 94 blocked owner proposals, 345 unresolved occurrence-relation proposals and
118 open conflicts factored into 29 challenge packages.
Ratified owners, canonical mutations and canonical gaps closed are all zero. A proposal is evidence
for an authority decision; it is never the decision itself.
