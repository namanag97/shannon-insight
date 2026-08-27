# SAN domain-to-library-to-compiler program DAG

This file is the concise program memory. The task ledger is its machine-readable
execution state. Candidate outputs never bypass the next audit or adjudication gate.

```text
                         SHARED CONSTITUTION / REGISTRY EVIDENCE
                                         |
                  +----------------------+----------------------+
                  |                                             |
                  v                                             v
       N1  NON-DATA ATLAS REBASE                    S1  SEMANTIC CONTRACT CANDIDATE A
   corpus + global web research                    independent semantic/domain model
                  |                                             |
                  v                                             |
       N2  ATLAS ACCEPTANCE AUDIT                              |
                  |                                             |
                  v                                             v
       N3  ACCEPTED ATLAS --------------------+     S2  LIBRARY/COMPILER CANDIDATE B
                                               \               /
                                                \             /
                                                 v           v
                                           S3  FINAL CONTRACT
                                               ADJUDICATION
                                                     |
                         +---------------------------+---------------------------+
                         |                                                       |
                         v                                                       v
             W1  SOVEREIGN-DOMAIN                                  D0  DATA/ANALYTICS
                WORK-PACKAGE REGISTRY                                  v0.2 ACCEPTANCE
                         |                                                       |
                         +---------------------------+---------------------------+
                                                     |
                                                     v
                                   PER ACCEPTED OWNER / CONTEXT
                                                     |
                     +-------------------------------+------------------------------+
                     |                                                              |
                     v                                                              v
             F1  DOMAIN FORGE                                             independent domain audit
   evidence -> boundary -> full DDD -> decisions -> contribution candidates        |
                     |                                                              |
                     +-------------------------------+------------------------------+
                                                     |
                                                     v
                                           L1  LIBRARY FORGE
                         0..N semantic/effect/interface library specifications
                                                     |
                                                     v
                                    reference implementations + conformance
                                                     |
                                                     v
                            registry admission + compiler contribution binding
                                                     |
                                                     v
                          portable closure -> target lowering -> runtime binding
                                                     |
                                                     v
                              mixed-industry positive and negative proof suites
                                                     |
                                                     v
                                     independent audit -> ratification decision
```

## Active parallel sessions

N1, S1, and S2 are independent and may run now. S1 must not see S2's output; S2 must
not see S1's output. N2 waits for N1. S3 waits for accepted N1/N2 output plus both S1
and S2 candidates.

## Data and analytics convergence

Data engineering and analytics remain one sovereign program family with multiple
bounded contexts. Its corpus has a separate evidence-heavy population track:

```text
data corpus contract candidate
  -> independent audit + three dissimilar pilots
  -> v0.2 revision requirements
  -> v0.2 corpus foundation builder
  -> independent v0.2 acceptance audit
  -> data/analytics domain work packages
  -> Domain Forges
  -> Library Forges
  -> shared registry/compiler/runtime proof chain
```

The current `session-01d` data foundation and data sovereign-library archive remain
candidates until the v0.2 requirements are reproducibly met. They are stress inputs,
not canonical outputs.

## Gates

1. **Atlas gate:** direct source reingestion, closed references, boundary competence,
   registry crosswalk, evidence diversity, and reproduced validation.
2. **Contract gate:** S1/S2 disagreements explicitly adjudicated; no category collapse.
3. **Work-package gate:** every candidate has an owner question, scope, dependencies,
   evidence posture, ambiguity set, and stopping/acceptance criteria.
4. **Domain gate:** strategic, tactical, temporal, epistemic, integration, decision,
   assurance, and operational semantics are explicit; boundary is independently tested.
5. **Library gate:** responsibility and decision completeness, purity/effect boundary,
   refusal algebra, compatibility/migration, conformance tests, and no provider leakage.
6. **Compiler gate:** contributions are typed and closed; omitted decisions refuse;
   no family-name branching; conflict and provenance survive every transformation.
7. **Execution gate:** target lowering and runtime/provider binding preserve portable
   meaning; observed claims include conditions and negative twins.
8. **Ratification gate:** independent evidence supports the exact state transition.

## Stop conditions

- Do not populate all candidate domains before N1 passes N2 and S3 is accepted.
- Do not infer libraries from context count.
- Do not infer implementation from a library spec.
- Do not infer compiler integration from a contribution schema.
- Do not infer runtime success from compilation.
- Do not claim global completeness while material coverage cells are untested.

