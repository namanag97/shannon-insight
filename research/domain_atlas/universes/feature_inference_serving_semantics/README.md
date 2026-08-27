# Feature and inference serving semantic kernel

This corpus resolves four coarse model-serving gaps into seven exact pure seams:

```text
observation spine + temporal contracts
          -> historical-cut planner -> historical-cut evaluator

source feature cut + observed online state
          -> materialization planner -> write/receipt protocol

entity keys + feature editions + purpose + deadline
          -> online-read protocol -> per-feature value/residual/freshness

eligible deployment revisions + route policy
          -> per-request revision router
          -> guarded rollout protocol -> non-authoritative route-change proposal
```

Physical query/dataflow execution, online stores, scheduling, entity identity, purpose authority,
model lifecycle approval, assurance, deployment, inference execution and business decisions remain
separately owned. Run `python3 build_corpus.py` and `python3 validate_corpus.py` in this directory.
All offers are specified but unimplemented, unqualified and non-portable.
