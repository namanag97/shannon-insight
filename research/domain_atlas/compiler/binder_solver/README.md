# Deterministic binder and constraint-solver candidate

This bundle specifies how a future SAN compiler may connect already-lowered intent requirements to
library, implementation, provider and target offers. It is a machine-readable research candidate,
not a solver, product selector, deployment tool or claim that the registries are complete. A result
is complete only relative to exact frozen snapshots. The binder never discovers a capability from a
vendor name, package name, spelling, tag or marketing category.

The research set contains 113 primary/authoritative sources spanning compiler construction,
SAT/SMT/CSP/MIP/ASP, package concretization, feature/configuration models, semantic/schema
subsumption, scheduling/resource allocation, proof checking, provenance and incremental builds.
The 2021–2026 innovation records deliberately exclude LLM and generative methods.
Model/LLM/agent assistance is an optional proposal source only: it cannot satisfy a parser,
typechecker, constraint, qualification, authorization, execution or receipt obligation, and removing
it leaves this complete binding path unchanged.

The bundle now imports the canonical provider/target registry as a digest-bound input. It projects
all 59 registry offers into the binder without changing their artifact, provider, target,
compatibility, assessment, exclusion or evidence identities. The eight original compiler-tool
candidates remain separate, producing 67 candidate offers in total. Projection may weaken an
upstream claim but is validated never to promote it.

It also imports the deterministic
[`model_class_adjudication`](../model_class_adjudication/README.md) snapshot. Solver/simulator
candidate enumeration begins only after a closed typed subproblem has matched sound multi-axis
class predicates. The binder consumes that result; it does not guess a class from the industry case,
vendor, library, LLM, or agent plan.

## The boundary

```text
declaration/language/analytical/observation/logical/assurance IR
                              |
                              v
                    exact requirements
                              |
                frozen registry/evidence snapshots
                              |
                              v
  +---------------------- BINDER (pure plan) -----------------------+
  | structural -> semantic -> feasible -> rank -> qualify -> admit  |
  |     |             |          |         |        |         |      |
  | candidates   implications SAT/SMT/CSP objectives receipts live  |
  | rejections   type/law     sat/unsat/?  frontier  scope   state  |
  +------------------------------+-----------------------------------+
                                 |
                                 v
            effect-free binding plan + proofs + typed gaps
                                 |
                       separate effect authority
                                 |
                                 v
              reservation/allocation/deployment/runtime probes
```

The seven center phases are non-collapsible:

```text
[1 structural matching]
  exact IDs/editions, arity, declared capability index
          |  does NOT prove meaning
          v
[2 semantic subsumption]
  direction, type, shape, operation, laws, authorized loss
          |  does NOT prove global feasibility
          v
[3 hard-constraint solving]
  SAT | UNSAT with evidence | UNKNOWN
          |  feasibility is not preference
          v
[4 optimization/ranking]
  lexicographic | Pareto | satisficing; declared authority
          |  selected is not qualified
          v
[5 qualification]
  exact artifact + target + config + test domain + checker receipt
          |  qualification is not capacity
          v
[6 admission/allocation]
  budget + quota -> admission -> reservation -> allocation -> lease/fence
          |  compile-time allocation is not observed behavior
          v
[7 runtime verification]
  probes, SLO/resource/policy receipts, drift and invalidation
```

Structural matching is intentionally weak. If a requirement named `ordered exact decimal aggregate`
and an offer named `aggregate` have the same port count, that creates at most a candidate edge. The
semantic phase must separately establish decimal domain, empty-input behavior, order dependence,
rounding, overflow, grouping grain, determinism and failure laws.

## Deterministic algorithm

```text
00 freeze exact registry/IR/evidence snapshots; verify digests
01 resolve stable identities and editions; never infer aliases
02 enumerate all structurally indexed offer edges in stable order
03 prove/contradict/retain-unknown each directional compatibility claim
04 create named hard atoms, soft preferences and support sets
05 solve hard instance -> SAT(model) | UNSAT(proof/core) | UNKNOWN(reason)
06 if UNSAT, retain sufficient core and advisory repair alternatives
07 if SAT, rank only feasible models under an authority-owned selection law
08 request exact-scope qualifications; documentation is not a receipt
09 keep documentation -> executed test -> independent appraisal -> qualification -> vertical
   acceptance as separate evidence transitions
10 reject stale, revoked, mismatched or uncheckable receipts
11 test hard budgets and quota admission separately from physical capacity
12 reserve and allocate; require finite lease/fence and release obligations
13 emit an effect-free plan; no compiler plan authorizes mutation
14 verify runtime claims and observe drift
15 map changes through support sets to requalification/rebinding
16 require incremental result == clean result for the same snapshots
```

Candidate enumeration, semantic proof and ranking preserve every rejected alternative. The final
tie-break is canonical stable identity, but only after all authority-owned objectives compare equal.
Changing a hard requirement into a weight is a compiler defect.

## Result and partiality model

```text
BindingResult = Bound(BindingPlan, ProofSet)
              | PartiallyBound(PlanFragment, NonEmpty<TypedGap>)
              | Unsat(SufficientCore, CheckStatus)
              | Unknown(Reason, PartialEvidence)
              | Refused(DomainDiagnostic)
```

Timeout, unsupported theory, proof-check failure, missing source occurrence, stale evidence and
resource uncertainty are `Unknown` or a typed refusal; none is `Unsat`. An unsat core is a sufficient
conflicting subset unless a separate receipt establishes minimality or minimum cardinality. A solver
model is independently checked before it becomes feasibility evidence.

## Identity, evidence and time

```text
stable semantic identity != edition != occurrence != content digest

claim --supported-by--> receipt
  |                        |
  | exact scope            +-- subject digest
  |                        +-- target occurrence
  |                        +-- configuration digest
  |                        +-- input/test domain
  |                        +-- checker identity/edition
  |                        +-- valid/recorded/retrieved/expiry time
  +-- invalidation triggers+-- limitations and raw observations
```

Evidence freshness is both time- and event-based. Artifact, dependency, target, configuration,
provider default, region, quota, budget, authority, vulnerability, checker or runtime behavior changes
can invalidate a receipt before its nominal expiry. Old bindings and receipts remain immutable history.

## Finite multi-objective budgets

Money, latency, energy, memory, storage, network, privacy, retry and operator-time budgets are typed
dimensions. Hard budgets participate in feasibility. Soft preferences participate only in ranking.
Weighted sums are refused unless an authority defines units, normalization, aggregation and acceptable
trade-offs. Otherwise the binder returns an explicit Pareto frontier or uses a declared lexicographic
order; it does not invent a universal utility function.

```text
resource demand != quota != hard budget != capacity offer
                != reservation != allocation != lease/fence != observed use
```

## Change and incremental rebinding

Every candidate, proof, decision, model, receipt and binding carries a support set. A changed key
invalidates its transitive dependants. Retaining an old receipt requires proving that no declared
trigger intersects its support set.

```text
change event -> changed exact keys -> support-set closure -> dirty claims
                                                       |
                     +---------------------------------+
                     v
       re-enumerate / re-prove / re-solve / re-qualify / re-admit
                     |
                     v
        semantic diff + migration plan + residual gaps
                     |
           clean-build equivalence check
```

Migration is a plan with state and in-flight-work dispositions; it is not permission to perform
effects. Rollback, roll-forward, dual-run, backfill, cutover and decommission remain separate modes.

## Examples and negative twins

`examples.jsonl` contains four unrelated verticals:

- an energy-operations day-ahead probabilistic net-load case;
- a banking counterparty-credit-risk SA-CCR calculation case.
- an oil-and-gas midstream nomination/capacity screening boundary derived from the canonical
  `energy.case.nomination_capacity_optimization` industry record.
- a manufacturing finite-capacity scheduling boundary derived from the canonical
  `mfg.case.finite_schedule` industry record.

Both positive traces stop at typed gaps because no exact, independently qualified offer/target
receipts exist. Their negative twins demonstrate forbidden inference: timezone/unit semantics from
field names, or legal entity/netting-set identity from counterparty display names. Performance or cost
ranking cannot rescue a semantically infeasible candidate. The pipeline twin additionally proves
that a broad `OR-Tools` project identity is not an exact solver offer, that “optimization” does not
imply a continuous-LP model class, and that MPSolver `INFEASIBLE` cannot be strengthened into a
proof of physical infeasibility.

The exact LP projection currently records:

```text
requirement                         OR-Tools/GLOP/MPSolver       highspy/HiGHS
safe status + checked objective     executed pass; typed gap    executed pass; typed gap
precise infeasible vs unbounded     executed failure; refuse    executed pass; typed gap

typed gap = independent appraisal and full qualification remain absent
```

The vertical case still stops earlier when its continuous-LP subproblem boundary is unproved; broad
network-flow, hydraulic, contract-priority or scheduling semantics are never forced into the LP
adapter merely because an industry record contains the word “optimization.”

The linked adjudication traces now make this split executable: the broad pipeline problem is
refused as LP, while the closed finite-coefficient screening cut is classified as continuous LP.
That classification still leaves provider qualification, target admission, vertical acceptance and
effect authority as separate blocking gates.

The exact CP-SAT projection retains both a falsification and its correction:

```text
requirement                         pre-enumeration adapter    corrected adapter
core integer/global/scheduling     scoped passes              scoped passes
UNKNOWN preservation               scoped pass                scoped pass
complete enumeration               executed failure; refuse   executed pass; typed gap

typed gap = independent appraisal, full qualification and manufacturing acceptance absent
```

A solution callback is not an exhaustive-enumeration request. The first occurrence observed one of
two solutions because its parameter surface omitted that intent. The second propagated the exact
enumeration parameter and the independent oracle observed both. The earlier evidence is retained;
the corrected adapter does not rewrite history or generalize beyond its package, digest,
configuration, target, fixtures and oracle.

## Library design and Rust applicability

The proposed libraries separate pure semantic model, structural enumeration, semantic compatibility,
constraint IR, solver SPI/adapters, objective selection, qualification, admission, invalidation and
trace contracts. Solver processes and allocation systems remain adapters behind explicit effect ports.

Rust can make many local illegal states unrepresentable: newtypes separate identity/edition/digest;
typestates prevent ranking before proof or allocation before qualification; enums preserve
`Sat/Unsat/Unknown/Refused`; sealed traits protect constitutional meanings; and `BTreeMap/BTreeSet`
support canonical iteration. Rust cannot prove that a provider claim is true, an ontology mapping is
authorized, a receipt is current, or a registry is complete. Those require external evidence and
domain authority.

## Files

- `metamodel.json`: closed constitutional model and phase separation.
- `binding-phases.jsonl`, `compiler-passes.jsonl`, `algorithms.jsonl`: deterministic pipeline.
- `constraint-kinds.jsonl`, `decision-points.jsonl`: hard/soft, authority and configuration model.
- `requirements.jsonl`, `offers.jsonl`, `requirement-offer-evaluations.jsonl`: explicit candidate
  bindings; all current offers remain non-bindable.
- `proof-contracts.jsonl`, `trace-contracts.jsonl`, `diagnostics.jsonl`: proof/refusal/explanation.
- `invalidation-rules.jsonl`: evidence freshness, change impact and incremental rebind.
- `library-boundaries.jsonl`, `rust-applicability.jsonl`: composable implementation boundaries.
- `examples.jsonl`: four verticals and their negative twins.
- `sources.jsonl`, `innovations-2021-2026.jsonl`, `gaps.jsonl`: research evidence and honest limits.
- `schemas/`, `manifest.json`: machine contracts and deterministic digests.

## Rebuild and validate

```text
python3 research/domain_atlas/compiler/binder_solver/build_bundle.py
python3 research/domain_atlas/compiler/binder_solver/validate_bundle.py
```

Validation requires no network or third-party package. It checks record shape and identity uniqueness,
source/evidence closure, exact phase order, reference closure, hard/soft separation, unknown
preservation, proof/diagnostic links, complete digest-bound provider/target projection, scoped
qualification-assessment linkage, non-bindable offers, exact safe/precise LP outcomes, positive
and falsifying/corrected CP-SAT outcomes, typed-gap termination, negative-twin symmetry,
innovation window, manifest digests and clean
deterministic regeneration.

## Honest limits

The model is a researched candidate. It does not contain complete canonical registries, formal
semantics for every enterprise law, exact deployed occurrences, executable qualification profiles,
qualified production solver/checker artifacts, complete independent appraisal, cost/capacity evidence,
migration implementations, scale results,
or two independent implementations. These are blocking gaps, not details the binder may guess.
