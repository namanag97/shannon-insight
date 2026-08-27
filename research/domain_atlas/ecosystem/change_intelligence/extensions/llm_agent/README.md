# Optional LLM/agent change-intelligence extension

This namespace retains exact model- and agent-specific change signals from the
supplied briefs without injecting them into deterministic core domains.  It is
optional and has one lawful dependency direction:

```text
llm_agent extension  ----imports---->  deterministic core substrate
deterministic core    ----X--------->  llm_agent extension
```

`change-signals.jsonl` records the Snowflake Cortex code-execution wrapper,
Snowflake CoCo automations, Snowflake model-assisted document functions, Cube
agent connectors and the OpenMetadata MCP wrapper. `substrate-mappings.jsonl`
maps each one to separately reviewed core evidence such as sandbox isolation,
caller identity, package policy, stage mounts, finite resource/cost limits,
scheduling, pagination or governed semantic queries. The mapping does not admit
model-dependent semantics into core and does not qualify a provider offer.

The effect chain is deliberately non-collapsible:

```text
model output
    != agent plan
    != validated claim
    != authorized tool intent
    != effect receipt
```

A model output has no effect authority. A plan is only a proposal. Validation
establishes a scoped claim, not permission. Authorization establishes a scoped
tool intent, not that an effect occurred. Only an occurrence-bound effect
receipt can evidence the outcome, including refusal, partiality or failure.

The root `build_corpus.py` generates this namespace and its schemas. The root
`validate_corpus.py` enforces the one-way dependency and the five distinct
effect-state identities.
