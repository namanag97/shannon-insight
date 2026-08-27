# Task planner

`program-tasks.jsonl` tracks program gates. `context-tasks.bootstrap.jsonl` contains
one provisional pipeline record for every bounded-context candidate in the current
v0.1.0 atlas. It is a planning inventory, not acceptance of those boundaries.

After N1 and its independent acceptance audit:

1. preserve old task IDs and source context IDs;
2. import accepted v0.2 context IDs;
3. record explicit `same_as`, `split_into`, `merged_into`, `rejected`, or `superseded_by`
   transitions from every bootstrap context;
4. create one work package only for each accepted or explicitly deferred owner question;
5. carry unresolved evidence, boundary, ownership, and terminology issues forward;
6. move tasks through gates only when their `required_evidence` references exist.

The planner does not assume one context equals one library. `architecture_disposition`
is unresolved until the domain specification can justify one of:

```text
semantic_library_family
effect_or_mechanism_library
interface_or_contract_only
profile
composition_or_card
application_or_product_package
provider_adapter
compiler_or_tooling_unit
research_only
reject
```

The canonical stage order is defined in `task-ledger.schema.json`. A task may remain
deferred without being treated as failed. A later stage cannot be completed before
all required predecessors and evidence references are complete.

