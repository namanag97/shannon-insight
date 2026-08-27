# Program artifact contract

The program passes governed artifacts between independent research and build gates.
Each artifact must identify its input editions, evidence posture, supersession status,
validation scope, unresolved issues, and exact downstream consumers.

| Kind | Answers | Must not claim |
|---|---|---|
| Research corpus | What claims and candidates were found, from what evidence? | Canonical boundaries or executable semantics |
| Domain atlas | What candidate semantic owners, contexts, relations, profiles, and vertical mappings exist? | One library per context or compiler admissibility |
| Atlas acceptance report | Which atlas records and checks survived independent reproduction? | That rejected/deferred material disappeared |
| Sovereign-domain definition contract | What must any full domain model state and prove? | A specific domain is already modeled |
| Domain work package | What bounded research/specification job exists for one candidate owner? | That its output will necessarily be a library |
| Domain specification | What vocabulary, laws, decisions, states, refusals, events, integrations, and evidence define one owner? | Runtime implementation or provider behavior |
| Library-family specification | What reusable public semantics and explicit decisions form an admissible library family? | One crate, one provider, or a running system |
| Reference implementation | What code realizes the accepted contract? | Universal portability without conformance proof |
| Compiler contribution | What typed requirements, offers, constraints, decisions, artifacts, diagnostics, and proofs can be composed? | A monolithic compiler stage or provider choice |
| Composition/card/profile | Which accepted units and decisions form a reusable capability or vertical specialization? | New semantic ownership by aggregation |
| Target lowering | How does portable meaning become a target-specific artifact without semantic drift? | Physical execution success |
| Runtime/provider binding | Which admitted implementation and resources satisfy the lowered requirements? | Changed business meaning or guessed intent |
| Proof package | Which positive and negative claims were observed under named conditions? | Ratification or certification unless separately granted |

The governing chain is therefore:

```text
evidence
  -> candidate claim
  -> adjudicated proposition
  -> accepted semantic owner/domain specification
  -> zero-or-more admissible library-family specifications
  -> zero-or-more conforming implementations
  -> typed compiler contributions
  -> closed application composition
  -> target lowering
  -> runtime/provider binding
  -> observed evidence and independent audit
```

