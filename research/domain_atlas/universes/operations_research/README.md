# Operations research and decision-science universe

This corpus makes operations research (OR) a first-class analytical universe. OR is the discipline of
formulating and improving decisions in constrained systems, often under uncertainty. It is not a KPI
catalog, not a synonym for one optimizer, and not an AI/LLM category.

The current edition is an evidence-backed **candidate atlas**, not a claim that the open world is closed.
It contains 287 named practices in 19 families, 36 bounded-context candidates, 79 official or primary
sources, 32 representative experts, 19 specialist-company patterns and 18 non-LLM innovation records
from the 2021–2026 review window. The compiler-facing projection adds 24 explicit decisions, 21
library boundaries, 21 requirements, 9 unqualified provider offers and 21 unexecuted qualification
profiles.

## The core distinction

```text
measurement / KPI                       operations research
-----------------                       -------------------
What happened?                          What decision is available?
How much?                               Who may decide or refuse?
Against which target?                   What is controllable?
                                        What is uncertain, and when known?
                                        What is feasible, preferred and harmful?
                                        What can be proved within the budget?
                                        What should be executed?
                                        What happened after execution?
```

[INFORMS defines OR around scientific problem analysis and decision making](https://www.informs.org/Resource-Center/INFORMS-Student-Union/FAQs-About-O.R.-Analytics),
and its methodology map spans decision analysis, dynamic programming/control, games, inventory,
networks, mathematical programming, queues, simulation, scheduling, utility/value and more. That is the
minimum breadth a horizontal platform must preserve, not a complete final taxonomy.

## Compiler-facing closure

```text
vertical business ontology + live operational state
                    |
                    v
             DecisionProblemIR
 actors | authority | actions | state | horizon | objective | constraints | uncertainty
                    |
                    v
       model/practice requirements + runtime budget
                    |
         +----------+-----------+
         |                      |
         v                      v
   model transformations   search/simulation policy
         |                      |
         +----------+-----------+
                    v
     provider offers -> qualification -> deterministic binding
                    |
                    v
 solve/simulate under cancellation, cost, work, memory and quality limits
                    |
                    v
               Result algebra
 invalid | unsupported | infeasible | unbounded | unknown | error
 feasible-unproved | bounded-quality | proved-optimal | cancelled-with-incumbent
                    |
                    v
 independent validation -> alternatives/sensitivity -> human authority
                    |
                    v
      commitment -> execution -> actual-vs-planned -> outcome feedback
```

The compiler must match **requirements to versioned offers**. It must not pick a solver because a vendor
page contains the word “optimization.” Official solver interfaces demonstrate why: OR-Tools MathOpt and
JuMP MathOptInterface distinguish termination reason, primal/dual result status, bounds, rays, limits and
result counts. An adapter that collapses these to `success: bool` loses decision-critical truth.

The first executed provider pilot falsified an additional identity collapse. `OR-Tools` is a suite,
not a solver offer; the tested chain is OR-Tools 9.15.6755 → GLOP → MPSolver Python adapter → one
native target occurrence. Its comparison subject is highspy 1.15.1 → HiGHS → another isolated
process. Both passed a six-fixture safe continuous-LP profile, but GLOP/MPSolver could not preserve
the distinction between infeasible and unbounded. The ACL safely reports
`infeasible_or_unbounded`; it may not strengthen that to `infeasible`. Same-process loading also
exposed an incompatible `libhighs` collision on the observed target. The two new exact offers
therefore remain non-bindable, unqualified and process-isolated; their generic project records are
discovery facades only.

The second exact pilot tests OR-Tools 9.15.6755 CP-SAT through its Python interface on one isolated
target. The corrected adapter passed bounded integer/Boolean, all-different/exactly-one,
fixed-interval/no-overlap scheduling, complete enumeration, invalid-model and limit-induced
`UNKNOWN` profiles. Its first retained configuration failed enumeration because a callback was
attached without requesting exhaustive search. Both receipts remain: adapter configuration is part
of the offer, and callback observation is not proof of completeness. The corrected run is still not
independently appraised, portable, production-qualified or accepted for a manufacturing schedule.

## Method-family coverage

| Family | Candidate count | What is kept distinct |
|---|---:|---|
| Framing | 12 | decision, authority, boundary, horizon, objective and constraint elicitation |
| Mathematical programming | 30 | LP/QP/conic/NLP/MIP/MINLP, bilevel, robust, stochastic and risk forms |
| Constraint and logic | 10 | CP, SAT, SMT, MaxSAT, ASP, lazy-clause and decision-diagram approaches |
| Exact algorithms | 16 | simplex/interior-point, branch/cut/price, exact DP and complete search |
| Decomposition | 12 | Benders, Dantzig-Wolfe, columns, scenarios, Lagrangian and ADMM protocols |
| Approximation and online | 8 | ratio, scheme, competitive, regret and streaming contracts |
| Constructive heuristics | 12 | greedy, insertion, savings, dispatch, packing and repair |
| Local search and metaheuristics | 23 | neighborhoods, memory, annealing, evolutionary and population search |
| Hyperheuristics and hybrids | 12 | portfolios, selection, configuration, matheuristics and simulation optimization |
| Networks and combinatorics | 18 | paths, flows, matching, trees, covering, packing, location and assignment |
| Routing | 17 | TSP/VRP variants, dynamic/stochastic, inventory, energy and crew routing |
| Scheduling | 18 | machine environments, projects, workforce, appointments, maintenance and repair |
| Inventory and planning | 14 | replenishment, multi-echelon, lot, capacity, S&OP, matching and assortment |
| Queues and reliability | 11 | congestion, capacity, failure/repair, availability and renewal |
| Simulation | 14 | Monte Carlo, DES, system dynamics, ABM, hybrid models and experiment validity |
| Sequential decisions and control | 13 | DP, MDP/POMDP, control, stopping, bandits and rolling horizon |
| Games, markets and revenue | 14 | equilibrium, mechanisms, auctions, matching, pricing and portfolios |
| Human decision | 13 | MCDA, utility, outranking, scenarios, elicitation, groups and override |
| Post-solve and qualification | 20 | feasibility, gaps, numerics, conflict, sensitivity, alternatives and feedback |

The family counts are an enumeration checkpoint. A record is admitted because it has a distinct problem,
method, assumption, evidence or result contract—not because facets were multiplied into artificial names.

## Heuristics are governed methods

```text
heuristic definition
  = solution representation
  + construction / neighborhood / move operators
  + feasibility preservation or repair
  + acceptance policy
  + intensification / diversification / restart
  + population or memory semantics, if any
  + random stream and seed
  + stopping and resource budget
  + incumbent/bound exchange
  + empirical qualification corpus
  + replay and failure semantics
```

“Heuristic” means that no general proof of optimality is supplied. It does not mean ungoverned, incorrect,
or “AI.” Exact search can time out with an incumbent; a heuristic can be the operationally correct choice
under a strict deadline. The result must say what was and was not established. PyVRP is a useful recent
example of an openly implemented, benchmarked hybrid genetic search for vehicle-routing variants; its
reported performance does not convert empirical quality into a universal optimality guarantee.

## Simulation is not optimization

Simulation describes the behavior of a declared model under experiments. It can estimate distributions,
stress a plan, compare alternatives or serve as an expensive response function inside simulation
optimization. It cannot by itself prove an optimum or prove that the real system matches the model.

```text
discrete-event simulation  -> processes, resources, queues and event time
system dynamics            -> aggregate stocks, flows and feedback
agent-based simulation     -> interacting modeled entities
                               (not LLM agents, not agentic software)
continuous simulation      -> differential/algebraic dynamics
multimethod simulation     -> explicit composition of two or more of the above
```

[AnyLogic's official material](https://www.anylogic.com/overview) independently exposes discrete-event,
system-dynamics and agent-based methods, while the Winter Simulation Conference archive supplies a broad
primary research trail for validation, verification and output analysis.

## Queueing is not simulation

Queueing analysis owns a declared arrival process, service process, class/station/buffer/routing
structure, discipline, initial/observation state, performance estimand and stability claim.
Simulation may execute a queue model, but it does not replace those semantics or the analytic and
conservation checks. The compiler projection therefore separates queue-model semantics, performance
methods, network methods, inference/calibration and independent validation. Little's law is applied
only under its stated conditions; an unstable or insufficiently observed system cannot silently
produce a steady-state result.

## Data OR consumes

OR depends on more than a feature table. A deployable decision problem may require:

- master/reference identity: products, locations, assets, resources, people, skills and calendars;
- live state: inventory, work in progress, positions, availability, commitments and faults;
- demand/work: orders, jobs, requests, forecasts, distributions, scenarios and priorities;
- topology and physics: networks, distances, travel times, capacities, yields and transition rules;
- economics and preference: cost, revenue, penalty, utility, targets, weights and service levels;
- authority and policy: eligibility, safety, labor, contractual, regulatory and approval constraints;
- time: event, validity, recording, planning horizon, lead time, duration and information revelation;
- uncertainty and dependence: scenario trees, distributions, ambiguity/uncertainty sets and stress cases;
- execution feedback: dispatched plan, overrides, exceptions, actual actions, outcomes and harms; and
- qualification evidence: benchmark instances, provider version, hardware, configuration and receipts.

Every value still needs units, missingness, provenance, as-of time, uncertainty and ownership. An optimizer
does not repair an ambiguous business ontology; it can turn ambiguity into a precisely wrong plan faster.

## Bounded contexts are not algorithms

The 36 records in `bounded-context-candidates.jsonl` are ownership hypotheses. Algorithms such as simplex,
tabu search or Benders decomposition are methods or implementation strategies. They become a bounded
context only if they own independent language, invariants, lifecycle and integration contracts after
context-map adjudication.

The strongest current candidates include decision-problem semantics, objective/preference, constraint
policy, uncertainty, model IR, transformation, decomposition, solver capability, qualification, selection,
solve execution, budget/stopping, reproducibility, proof, approximation guarantees, heuristic semantics,
simulation model/experiment, infeasibility diagnosis, independent validation, human decision, deployment,
execution and outcome feedback.

## Companies are evidence, not taxonomy authorities

`companies.jsonl` distinguishes solver/modeling companies, simulation companies, horizontal decision
operations, vertical optimization products and custom solution firms. Official vendor pages establish what
the provider claims to sell; they do not independently establish performance or outcomes.

MathCo is specifically classified as an **analytics solution-company pattern**. Its published manufacturing
material confirms that it combines data pipelines, heuristic algorithms, scheduling models, operational
interfaces and claimed outcomes. That is valuable evidence for solution composition. It is not authority
for the neutral OR vocabulary, and its AI-heavy positioning is not imported into this corpus's core.

## Recent non-LLM innovation themes

The five-year evidence supports several concrete directions:

- practical first-order LP at very large scale through PDLP;
- GPU first-order LP through cuPDLP and emerging HiPDLP work;
- hybrid CP-SAT-LP portfolio architectures;
- richer solver-neutral model/result interfaces such as MathOpt;
- open solver engineering across SCIP, HiGHS and Clarabel, including Rust interfaces;
- global nonlinear/MINLP expansion in commercial solvers;
- reusable high-performance domain heuristics such as PyVRP;
- stronger containerized benchmark and solver-qualification protocols; and
- productization of model/run governance (“DecisionOps”), still lacking a neutral standard.

Each innovation record separates peer-reviewed/open evidence, official release evidence, roadmap evidence
and provider marketing claims. “Recent productization of an older idea” is not mislabeled as invention.

## Artifacts

- `methods.jsonl` — 287 provider-neutral practice candidates with intent, I/O, assumptions, guarantees,
  result states, budgets, evidence, compiler implications and gaps.
- `bounded-context-candidates.jsonl` — 36 ownership hypotheses; none are automatically promoted from a
  method or vendor feature.
- `sources.jsonl` — 79 primary or official evidence records with explicit authority limits.
- `experts.jsonl` — 32 representative experts and the reusable design lesson from each body of work.
- `companies.jsonl` — 19 specialist-company patterns with claims separated from verification posture.
- `innovations.jsonl` — 18 non-LLM innovation candidates for 2021–2026.
- `decision-points.jsonl` — explicit optimization, queueing and simulation choices; provider defaults cannot
  silently resolve them.
- `library-boundaries.jsonl` — provider-neutral optimization, queueing and simulation contributions with
  single semantic owners, effect boundaries and removal seams.
- `compiler-requirements-offers.jsonl` — one requirement per library, six non-bindable provider
  project facades, and three exact executed-but-unqualified adapter/artifact offers.
- `qualification-receipts.jsonl` — executable-profile templates; every result list is empty in this
  edition and therefore proves no provider capability.
- `build_corpus.py` — reviewable authoring source and deterministic JSONL generator.
- `validate_corpus.py` — structural, referential, coverage and exclusion checks.

Regenerate and validate with:

```bash
python3 research/domain_atlas/universes/operations_research/build_corpus.py
python3 research/domain_atlas/universes/operations_research/validate_corpus.py
```

## Explicit gaps and next adjudication

- This is broad enumeration, not proof of global completeness.
- Method aliases, theorem preconditions, problem-variant inheritance and cross-family relations need a
  dedicated relation graph.
- Expert and company records are representative open-world seeds, not “all experts” or rankings.
- Several company records still rely only on provider evidence and need independent implementation and
  customer/outcome checks.
- Each method needs provider-offer conformance fixtures and at least two unrelated vertical bindings.
- Bounded-context ownership must be reconciled with the global data, runtime, workflow, authority,
  economics and application context maps before product boundaries are derived.
- A neutral DecisionProblemIR, Result algebra and SolverOffer contract should be prototyped only after that
  ownership adjudication, then tested on unrelated cases such as counterparty-credit mitigation,
  production scheduling, emergency-department capacity and energy-system dispatch.
