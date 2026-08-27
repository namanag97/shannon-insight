# P3S state/change coordinate ontology and member rebase

This package prevents a library-wide `Status` or `State` abstraction from
collapsing unrelated lifecycles. A single library may own an immutable
definition edition, a mutable domain aggregate, a workflow run, an execution
attempt, a desired-state resource, an observation, and an external effect
receipt. Each is a separately identified state subject.

The coordinate contract binds:

- bounded context, subject identity and state-subject archetype;
- lifecycle identity and edition;
- active state/configuration and assertion position;
- revision, history cut and completeness;
- trigger, guard, authority and expected revision;
- emitted facts, proposed effects, receipts and acceptance;
- refusal precedence, concurrency and compensation.

Twelve subject archetypes cover domain aggregates, immutable successors,
resource representations, workflows, executions, desired/observed control,
artifacts/models/schemas, credentials, evidence, table snapshots, stream
progress and external effects. Thirty-one transition kernels factor recurring
behavior without declaring that any kernel applies to a member.

The original flat facets remain lexical discovery projections. They cannot
choose a subject, lifecycle, assertion position, transition, history model,
effect stage or applicability decision.

All 629 targeted member occurrences are preserved in
`member-state-routes.jsonl` and partitioned by
`member-research-clusters.jsonl`. Of those, 84 have lexical discovery signals
and 545 retain explicit member-state evidence vacancies. No owner, member
applicability, exact contract or gap closure is asserted.
