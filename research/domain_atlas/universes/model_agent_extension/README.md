# Optional model and tool-agent extension universe

Status: evidence-backed **candidate research corpus**, not an application, autonomous-agent product,
provider endorsement, completeness claim, or production qualification.

This package gives generative models and tool-using agents a precise, removable place in the data
and analytics domain atlas. It does not create an “AI version” of every deterministic bounded
context. Instead it owns only the genuinely additional semantics introduced by nondeterministic
generation, prompts and context, model invocations, generated proposals, retrieval grounding,
tool-call proposals, optional memory, evaluation, and provider adaptation.

The most important architectural law is one-way dependency:

```text
                    OPTIONAL EXTENSION
 task / prompt / context / model edition / invocation
 generated proposal / claim / plan / tool-call proposal
 retrieval / grounding / memory / eval / drift / fallback
                            |
                            | imports typed contracts; never grants authority
                            v
                 DETERMINISTIC CORE (authoritative)
 identity / DDD meaning / canonical adjudication / binding
 authn / authz / approval / delegation / revocation
 resource admission / scheduling / cancellation / budgets
 effect intent / execution / receipt / reconciliation
 provenance / evidence / quality / provider qualification

Allowed dependency: extension -----------------------> core
Forbidden dependency: core - - - - - - - - - - - -> extension

Delete extension: deterministic declarations, plans, effects and proofs remain valid.
Delete core: extension cannot authorize, execute, settle, prove or reconcile anything.
```

Classical predictive and statistical ML is a **neighboring core universe**, not a member of this
extension. Study design, target/label semantics, features, estimands, estimators, training,
fitted-model identity, calibration, predictive evaluation, drift and qualified inference kernels
belong to `method_kernels` and related analytical-method domains. A predictive model does not
become an “agent” merely because an API invokes it.

```text
classical predictive ML                    optional model/agent extension
-----------------------                    ------------------------------
study / estimand                           task / prompt / context
features / labels                          generated proposal / claim
estimator / fitted model        <---->     generative invocation / tool proposal
calibration / predictive error             retrieval / memory / agent evaluation
qualified inference kernel                 provider model adapter
              \                              /
               \                            /
                +---- deterministic core ---+
```

## Non-collapsible compiler chain

Generated language never crosses directly into an effectful system:

```text
declared task intent
        |
        v
exact model + prompt + context + target occurrence
        |
        v
model invocation receipt
        |
        v
generated output
        |
        +---- generated claim ---- evidence link ---- validation verdict
        |
        +---- generated plan / tool-call proposal
                         |
                         v
                 deterministic checks
            schema / invariants / authority / budget
                         |
                         v
                   core effect intent
                         |
                  authorized execution
                         |
                         v
                   core effect receipt
                         |
                         v
                 observed reconciliation
```

The following identities and meanings must remain distinct:

- task identity ≠ invocation identity ≠ retry identity;
- model family ≠ model edition ≠ provider deployment occurrence;
- prompt identity ≠ prompt edition ≠ variable binding ≠ concatenated text;
- context relevance ≠ instruction authority;
- input accepted by an API ≠ semantically valid input;
- JSON/grammar conformance ≠ domain validity ≠ factual truth;
- tool definition ≠ tool visibility ≠ selection ≠ authorization ≠ execution;
- generated proposal ≠ decision;
- generated claim ≠ validated claim;
- plan ≠ effect intent ≠ effect receipt;
- retrieval result ≠ trusted instruction ≠ admitted evidence;
- citation presence ≠ entailment ≠ truth;
- memory retrievability ≠ disclosure authority;
- cancellation request ≠ cancellation completion;
- retryable model call ≠ retry-safe downstream effect;
- provider API compatibility ≠ semantic portability;
- model weights ≠ qualified local serving target;
- low temperature or a seed ≠ deterministic replay;
- benchmark score ≠ target-workflow fitness;
- model-judge score ≠ ground truth;
- verbal confidence ≠ calibrated probability.

Every material unknown fails closed or takes an explicitly declared non-model path. A generated
proposal can be useful, but it cannot create identity, validate itself, authorize itself, spend an
unadmitted budget, invoke a protected effect, write durable memory, or author its own receipt.

## Coverage

`manifest.json` records the exact generated counts:

| Surface | Count |
|---|---:|
| bounded-context candidates | 71 |
| typed operations | 142 |
| decision points | 71 |
| non-functional/semantic laws | 71 |
| operations + decisions + laws | 284 |
| primary sources | 104 |
| source-to-context evidence mappings | 104 |
| library/adapter/oracle boundaries | 30 |
| optional compiler requirements | 30 |
| declared, unqualified provider/local offers | 6 |
| unexecuted qualification profiles | 30 |
| compiler mappings | 71 |
| proof contracts | 71 |
| core imports | 12 |
| innovations, 2021–2026 | 22 |
| explicit research gaps | 25 |
| useful examples / negative twins | 2 / 6 |

The 71 candidate contexts cover:

- task, model-family, model-edition, provider-occurrence, prompt, context and invocation identity;
- input, output, multimodal, streaming, structured-generation and tool schemas;
- sampling, nondeterminism, completion/refusal/truncation and replay limits;
- optional retrieval requirement, scope, query, result, grounding and attribution;
- proposal, plan, generated claim, validation, effect-intent and effect-receipt boundaries;
- human/machine authority, approval, delegation, tool authorization and bounded orchestration;
- conversation state, working memory, durable memory, isolation and loss-aware compaction;
- token, time, cost, quota, cancellation, retry and fallback contracts;
- evaluation design, datasets, graders, uncertainty, failure slices and adversarial tests;
- prompt injection, exfiltration, secrets, retention and safety-policy intervention;
- trace/provenance, monitoring, drift, invalidation, rollout and provider portability;
- exact local/remote target binding and qualification.

Retrieval is not mandatory. `retrieval_requirement` asks whether external evidence is needed for the
task. Static transformations, deterministic lookups, already-admitted evidence and tasks where
retrieval would expand disclosure can use an explicit no-retrieval path.

## Compiler contract

Each bounded context emits one provider-neutral requirement/offer mapping and one proof contract.
The physical binder needs an exact model edition or an explicitly typed unresolved alias, prompt
edition, provider deployment/target occurrence, resource limits, data-processing posture, and
qualification receipts for the relevant task and failure slices. Provider documentation is a
declaration, not a qualification receipt.

The normalized binding projection is deliberately weak in authority: all 30 requirements are
optional or intent-required and carry `fallback_law: omit_optional`; all six provider/local offers
are declarations with empty conformance receipts; and none may satisfy a deterministic-core
requirement. Absence of a qualified offer therefore removes the extension stage instead of
weakening a parser, solver, validator, authorization rule or evidence obligation.

```text
portable extension requirement
       |
       +-- task / modality / schema / tool / state requirements
       +-- quality / safety / uncertainty / latency / cost thresholds
       +-- retention / region / authority / effect prohibitions
       |
       v
provider-neutral offer shape
       |
       v
exact adapter + model edition + deployment + target occurrence
       |
       v
qualification receipts for task x slice x target x edition
       |
       +-- pass -> bind optional extension stage
       |
       +-- missing/expired/inconclusive -> refuse or explicit non-model path
```

An alias change, prompt change, tool-schema change, safety-policy change, retrieval-corpus change,
target change, quantization/runtime change, evaluation-data invalidation, or material behavior drift
can invalidate qualification. A successful historical evaluation is not silently carried forward.

## Library boundaries

The 30 candidate boundaries are intentionally smaller than an agent framework:

```text
pure semantic contracts
  task intent | identities | prompt | context | schemas | proposals | retrieval
        |
        +---- test oracles
        |       structured output | citation | eval | adversarial | portability
        |
        +---- provider port ---- provider adapters
        |                          OpenAI / Anthropic / Gemini / Bedrock /
        |                          Microsoft Foundry / local inference
        |
        +---- runtime mechanisms
        |       compaction | retry/cancel | qualification monitoring
        |
        +---- deterministic-core adapters
                authority | effect intent | effect receipt | budgets | provenance
```

Provider adapters own only representation and behavior mapping for an exact API/profile. They do
not own business meaning, credentials, authorization policy, model qualification, resource policy,
tool effects, or provider portability. Test oracles perform no production effects. Pure libraries
perform no I/O. Removing one provider adapter cannot change the semantic core.

## Security and authority posture

External content—including email, documents, web pages, tool results, retrieved chunks, model
messages and peer-agent messages—is data unless a core-recognized principal grants it instruction
authority. Prompt text cannot upgrade that authority. Tool access uses least functionality, least
privilege, audience-bound credentials and per-effect policy checks. Secret values do not enter model
context when a reference or core-side binding suffices.

Streaming consumers must not interpret an observed partial delta as a completed, schema-valid or
safety-admitted result. Durable memory requires explicit identity, tenant, purpose, consent,
retention and revocation. Provider storage flags and documented retention policies are retained as
claims until occurrence-specific evidence supports them.

## Evidence posture

`sources.jsonl` contains provider documentation, open protocol/standards texts, government risk
frameworks, official security-project guidance, official open-source project documentation and
original research papers. All records are primary sources and carry a use limit: a provider page
supports only its documented interface; a benchmark paper supports only its evaluated setting; a
security taxonomy identifies risks but does not prove a defense; and an API shape does not define
the canonical domain model.

The source set includes official OpenAI documentation for exact API mechanics, alongside Anthropic,
Google, AWS, Microsoft, Cohere, Hugging Face and vLLM sources; MCP, A2A, OpenAPI, JSON Schema,
OAuth, W3C PROV, OpenTelemetry and SCITT specifications; NIST and OWASP guidance; and original
papers on RAG, ReAct, Toolformer, structured decoding, evaluation, uncertainty, executable-agent
benchmarks, prompt injection, serving and speculative decoding.

The 25 gaps are not cosmetic TODOs. Cross-provider semantic equivalence, exact-edition identity,
seed replay, structured truth, tool-result taint, prompt-injection elimination, causal effect
attribution, human-approval quality, end-to-end memory deletion, compaction equivalence, citation
entailment, uncertainty calibration, grader validity, contamination, evaluation transfer, mutable
safety layers, cost settlement, cancellation finality, partial-stream safety, fallback equivalence,
local-target qualification, provider retention, multi-agent delegation, protocol-version drift and
independent security review remain open until exact evidence closes them.

## Examples and negative twins

`examples/useful-examples.json` contains:

1. an evidence-synthesis flow with no effects, where retrieved content remains untrusted and claims
   are returned as validated or unvalidated;
2. a proposed data repair where the model drafts only a proposal, deterministic validation and
   exact human approval precede a core effect intent, and a core receipt plus reconciliation—not
   generated narration—establishes what happened.

`examples/negative-twins.jsonl` tests generated versus validated claims, tool calls versus effect
receipts, retrieved data versus authorized instructions, aliases versus immutable editions, model
retry versus effect replay, and memory availability versus disclosure authority.

## Files

- `metamodel.json` — identities, binding chain and constitutional separation laws.
- `contexts.jsonl`, `operations.jsonl`, `decisions.jsonl`, `laws.jsonl` — DDD candidate model.
- `compiler-mappings.jsonl`, `proof-contracts.jsonl` — fail-closed binding and proof surfaces.
- `core-imports.jsonl` — the one-way dependency map into deterministic universes.
- `classical-predictive-ml-boundary.json` — explicit neighboring-domain ownership.
- `library-boundaries.jsonl` — 30 pure/runtime/adapter/oracle seams.
- `compiler-requirements-offers.jsonl` — 30 removable requirements and six declared, unqualified
  provider/local offers; no offer satisfies a deterministic-core contract.
- `qualification-receipts.jsonl` — 30 unexecuted qualification profiles with empty results.
- `sources.jsonl`, `source-coverage.jsonl`, `innovations-2021-2026.jsonl`, `gaps.jsonl` — evidence, explicit semantic support routing, change and uncertainty.
- `examples/` — two useful scenarios and six semantic negative twins.
- `schemas/` — Draft 2020-12 schemas for every compiler-facing JSONL record family.
- `build_corpus.py` — deterministic generator with byte-for-byte `--check` mode.
- `validate_corpus.py` — schema, identity, reference, threshold, direction, law and regeneration
  validator.

## Rebuild and validate

```bash
python3 research/domain_atlas/universes/model_agent_extension/build_corpus.py
python3 research/domain_atlas/universes/model_agent_extension/validate_corpus.py
python3 research/domain_atlas/universes/model_agent_extension/build_corpus.py --check
```

If `jsonschema` is installed, the validator additionally checks every compiler-facing record against
its Draft 2020-12 schema. Without it, all dependency-free structural, reference, threshold,
constitutional-law, optionality and deterministic-regeneration checks still run.
