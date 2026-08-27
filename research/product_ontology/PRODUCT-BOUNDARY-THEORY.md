# Product-boundary theory

## 1. Product definition

A product is a **governed, independently consumable promise of outcomes to a defined user**, with
an owned lifecycle, interface, authority boundary, service posture, evidence and exit path.

```text
ProductIdentity =
    UserPopulation
  x JobAndOutcomeContract
  x AdoptionAndExitBoundary
  x SemanticOwner
  x AuthorityBoundary
  x LifecycleAndCompatibility
  x OperationalAndFailureBoundary
  x EconomicBoundary
  x PublishedInterfaces
  x EvidencePosture
```

This is an identity tuple, not a formula for multiplying product counts. A material change to one
coordinate is evidence for a split, but the complete split/merge test must still be applied.

## 2. Things that are not automatically products

| Candidate | Why it is not automatically a product |
|---|---|
| Bounded context | A language/consistency boundary can support several products or only one part of one. |
| Library/crate | An implementation ownership unit may have no direct user, outcome or service lifecycle. |
| Capability | A selectable behavior can be offered by several products and composed inside one product. |
| Machine | A typed compositional unit is normally below the adoption boundary. |
| Standard/protocol | It defines interoperability but does not itself operate a promise for a user. |
| Resource | Compute, storage and networking become products only when wrapped in an owned service promise. |
| Dashboard/application | A user interface can be one channel into a product or a vertical solution. |
| Vendor SKU | Commercial packaging may bundle sovereign products or split one product by pricing. |
| Architecture style | Lakehouse, mesh, fabric, lambda and medallion are compositions/patterns. |
| Industry name | Sports, oil, healthcare and retail normally select packs, not new horizontal engines. |

## 3. Product split test

Score every candidate boundary `0 = shared`, `1 = ambiguous`, `2 = independently distinct`.

1. **User:** Does it serve a materially different user population?
2. **Job:** Does the user hire it for a different job and outcome?
3. **Adoption:** Can it be adopted, replaced or removed independently?
4. **Semantics:** Does it answer a different sovereign question and own different meanings?
5. **Authority:** Does it exercise a distinct authority or trust boundary?
6. **Lifecycle:** Can it version, migrate, deprecate and release independently?
7. **Operation:** Does it have a distinct SLO, capacity model, on-call owner or failure domain?
8. **Economics:** Is cost/usage measured and governed independently?
9. **Interface:** Does it expose a stable contract usable by multiple compositions?
10. **Market evidence:** Do multiple interchangeable implementations exist or plausibly exist?

Interpretation:

```text
0-6    normally merge into a capability/module
7-12   unresolved; retain as candidate and gather evidence
13-16  presumptive product boundary
17-20  strong product boundary
```

No numeric threshold overrides semantic ownership. Two candidates that would own the same meaning
must be merged, narrowed or related through an explicit translation contract.

### 3.1 Evidence-carrying scores

A split-test number without scoped evidence is invalid. Every coordinate must retain:

```text
SplitCoordinate =
    Axis
  x Score(0..2)
  x EvidenceReferences
  x ClaimScope
  x Confidence
  x ResidualEvidenceNeeded
```

Official product packaging may support user, adoption, operation or market coordinates. It does
not establish semantic ownership or conformance. A specification may support semantic, interface
or compatibility coordinates. It does not establish an operated product, adoption or SLO. Local
prose and repository shape cannot receive an independent score of `2`.

The verdict remains a candidate until every decisive evidence item is current, independently
reviewed and connected to an exact artifact or provider edition.

## 4. Product merge test

Merge candidates when most of these are true:

- the same users consume them for one indivisible outcome;
- neither has a meaningful independent adoption or exit path;
- they share one semantic owner, lifecycle and compatibility relation;
- separate operation would not isolate failure, authority, cost or scale;
- the apparent split is a framework, deployment or team artifact;
- provider alternatives replace the combined promise rather than either part independently; and
- separation would expose accidental implementation complexity to users.

## 5. Mandatory kinds

```text
market_product             externally purchased outcome promise
internal_platform_product  internally consumed self-service promise
engine_product             independently embedded computational promise
control_plane_product      desired-state, policy and reconciliation promise
provider_product           operated generic resource/service promise
data_product               governed data or analytical publication
experience_product         coherent user experience over other products
```

`Suite` is packaging. `SolutionPack` is a vertical composition. Neither re-owns the semantics of
its products.

## 6. Three orthogonal decompositions

The portfolio must retain three graphs instead of forcing one hierarchy:

```text
Semantic graph       who owns each meaning and invariant
Product graph        who promises which outcome to which user
Implementation graph which machines/libraries/providers realize the promise
```

The composition compiler links the three through typed offers and requirements. It must never
infer that a repository dependency establishes semantic authority or that a suite owns all the
meanings of its contents.

For architecture labels such as lakehouse, the minimum non-collapse chain is:

```text
pattern -> suite -> product -> capability -> semantic contract
                                      |             |
                                      v             v
                              provider offer   library contract
                                      |             |
                                      +--> qualified implementation
```

An arrow never promotes the target into the source kind. In particular, a table-format standard
or semantic library is not an engine product, and a managed table service does not make its
maintenance algorithm a product.

## 7. Product completeness

The 110-point truth contract is evaluated for every product with one of:

```text
REQUIRED
CONDITIONAL(condition)
PROHIBITED(law)
INAPPLICABLE(reason, evidence)
UNDETERMINED(owner, evidence_needed)
```

Silence is invalid. Applicability does not imply that every product implements every concern. A
pure statistical engine can mark UI and disaster recovery inapplicable; an operated lakehouse
experience cannot.

## 7.1 No one-method decomposition

DDD is necessary for deep semantic modeling but is not a universal boundary algorithm. It answers
where a model and ubiquitous language are applicable, how model owners relate, and where
transactional invariants live. It does not by itself prove customer value, independent adoption,
market evolution, service levels, physical fault domains, commonality/variability, security,
safety, or mathematical correctness.

Likewise, the following outputs must not be promoted into one another:

```text
Wardley component       != product != capability
business capability     != process != bounded context
EventStorming cluster   != aggregate != ratified context
BPMN pool               != team != service
ontology module         != source truth != product
C4 container            != bounded context != deployment requirement
feature                 != runtime flag != library != product
team boundary           != semantic owner
SLO/failure domain      != user outcome or meaning
formal specification    != domain evidence or market evidence
```

The admissible boundary method is an ensemble:

```text
strategy/value       Wardley + capabilities/value streams + JTBD/product discovery
domain meaning       DDD + EventStorming + Domain Storytelling + terminology
work behavior        BPMN + CMMN + DMN + state/process formalisms + process mining
information          conceptual/fact/data models + ontology + constraints + contracts
software structure   C4 + arc42 + ports/adapters + dependency/change analysis
reuse/variability    FODA + product lines + variation/decision models
formal correctness   Alloy + TLA+ + contracts + property/model/proof methods
system/trust         SysML + STPA + threat/privacy/failure analysis
operation/economics  SRE + capacity/resilience + FinOps
empirical challenge  fieldwork + literature + code/log/usage mining + red teams
analytics            measurement + statistics + causal + OR + simulation formulation
```

Each method contributes claims only inside its evidence scope. A candidate remains
`UNDETERMINED_NOT_PASS` when an applicable lens is missing. Agreement supports a bounded verdict;
disagreement is retained as a hotspot rather than averaged into a score. The machine-readable
catalog and first triangulation live in `boundary_method_ensemble/`.

### Boundary discovery order

1. Observe concrete work, users, harms, source occurrences, decisions, failures and effects.
2. Apply several discovery methods in their native form; do not force one metamodel during elicitation.
3. Normalize claims into typed evidence while retaining method, scope, time and uncertainty.
4. Derive bounded contexts from language/model applicability and translation requirements.
5. Derive aggregates from synchronous invariants, not from services or tables.
6. Derive libraries from conceptual contours, closure of operations, variation and effect seams.
7. Independently derive products from users, outcomes, adoption, operation, economics and exit.
8. Join these graphs and adjudicate overlaps, imports, authority and provider boundaries.
9. Falsify with unrelated verticals, observed systems, negative twins and formal counterexamples.
10. Re-run after implementation and production evidence; no decomposition is final merely because it is documented.

## 8. Automation modality is an orthogonal axis

`AI`, `LLM` and `agentic` are implementation modalities, not prefixes that create new meanings,
bounded contexts, capabilities or products. A declared operation may be realized by one or more
qualified modalities:

```text
human procedure | deterministic rules/algorithm | operations research/statistics
                | classical predictive model | generative model | tool-using agent | hybrid
```

The modality is selected only after the operation's input/output types, invariants, authority,
budgets, evidence and acceptance oracle exist. Adding a model or agent therefore does not rename
`catalog`, `quality`, `forecast`, `reconciliation`, `optimization` or any other domain concept.

Automation also does not discharge the research and construction obligation. Vocabulary must
still be enumerated, competing meanings adjudicated, invariants and state transitions written,
algorithms selected, source evidence retained, negative twins tested, and provider behavior
qualified. A model or agent may accelerate this work or propose a candidate artifact, but the
artifact enters the corpus or an executable plan only through the same typed, reviewable,
deterministic acceptance path as a human-authored candidate. Expensive semantic work does not
become optional merely because a capable generator exists.

An LLM- or agent-centered candidate must pass the same product split test as every other candidate.
If it does not have independent users, adoption, operation, support, economics, exit and semantic
boundaries, it remains a capability, provider, library or feature of an existing product.

The compiler must retain these identities:

```text
model output / agent proposal != validated claim
validated claim               != authorized effect intent
authorized effect intent      != executed effect
execution receipt             != business outcome
```

The deterministic core owns parsing, typing, constraints, authority, policy, effect execution,
state transitions, receipts and acceptance. Optional model/agent providers may propose, rank,
extract, generate or plan through typed ports. Removing them must either leave a valid core plan or
produce an explicit `capability_unavailable` gap—never silently weaken a law or fabricate a result.

`Deterministic core` does not mean that every analytical method is closed-form. Statistical,
probabilistic, predictive, heuristic, simulation and optimization methods remain first-class when
the declared intent requires them. Their stochasticity or approximation must be explicit in the
method contract, seeds and uncertainty where applicable, validation evidence, operating envelope
and refusal behavior. They are not silently converted into LLM or agent capabilities.

Each use site declares the modality posture as `PROHIBITED`, `OPTIONAL`, `REQUIRED_BY_INTENT`, or
`UNDETERMINED`; no global default adds AI everywhere. Qualification of a stochastic modality adds
model/provider edition, evaluation slices, uncertainty, drift, prompt/tool security, latency, cost,
fallback, human-review and replay evidence without replacing ordinary domain conformance.

## 9. Research and annealing procedure

1. Enumerate candidates from lifecycle, plane, workload, modality, actor and authority axes.
2. Map reference architectures, standards, incidents, products and independent implementations.
3. Apply the split test and publish the evidence for each score.
4. Overlay at least two unrelated enterprise scenarios.
5. Detect duplicated semantic owners, hidden shared state and missing exit paths.
6. Merge, split, rehome or reject candidates without preserving compatibility aliases.
7. Re-run graph closure and the 110-truth applicability audit.
8. Keep the bounded verdict and residual evidence gap; never claim global completion.

## 10. Initial falsifiers

The model is wrong if any of the following occurs:

- switching sports to oil requires changing a horizontal product's owned meanings;
- replacing a query engine requires replacing table identity or business metrics;
- a catalog can authorize a table commit without an explicit authority contract;
- an analytical result becomes a business fact without returning through the owning application;
- two products both claim ownership of metric, dataset, identity or policy semantics;
- a supposedly independent product has no independent adoption, lifecycle or exit;
- a supposedly single product contains incompatible SLO, failure or authority boundaries; or
- a compiler can close a solution while product requirements remain unresolved.
