# Operations research is a first-class analytical universe

Operations research (OR) is not a synonym for a dashboard and is broader than one optimization
solver. It turns an operational decision under constraints and uncertainty into a model, a search or
solution procedure, a qualified result and an action policy.

```text
real decision system
      |
      v
decision semantics
  actors | controllable decisions | state | horizon | objective(s) | constraints | uncertainty
      |
      v
model families
  mathematical programming | constraint programming | networks | queues | stochastic processes
  simulation | inventory | scheduling | routing | games/markets | decision analysis | control
      |
      v
solution strategy
  +-----------------+----------------------+--------------------+-------------------+
  | exact           | approximation        | heuristic          | hybrid            |
  | proof/bound     | quality guarantee    | empirical quality  | matheuristic       |
  | branch/cut/etc. | problem-specific     | time-budgeted      | exact + heuristic |
  +-----------------+----------------------+--------------------+-------------------+
      |
      v
qualified solution
  feasibility | objective(s) | bounds/gap | stability | sensitivity | fairness | explanation
  runtime/cost | randomness/seed | reproducibility | alternatives | constraint trade-offs
      |
      v
decision policy + execution + outcome feedback
```

## Required horizontal bounded contexts

The candidate atlas must eventually adjudicate distinct owners for at least:

1. decision-problem semantics;
2. decision variables, domains and state;
3. objectives, priorities and multi-objective preference;
4. hard, soft, chance and policy constraints;
5. deterministic, stochastic and robust uncertainty semantics;
6. mathematical/constraint/network/simulation model IRs;
7. transformations, relaxations, decompositions and linearizations;
8. solver requirements, offers, qualification and selection;
9. exact algorithms and proof/bound receipts;
10. constructive heuristics and local search;
11. metaheuristics, hyper-heuristics and algorithm portfolios;
12. matheuristics and simulation-optimization hybrids;
13. runtime budgets, stopping rules, cancellation and reproducibility;
14. infeasible/unbounded/unknown result semantics;
15. solution validation, sensitivity and post-optimality analysis;
16. alternative-solution and solution-pool semantics;
17. human approval, override and explanation;
18. deployment as a decision policy, not just a one-time solve;
19. actual-versus-planned outcome reconciliation; and
20. model drift, refit, replay, rollback and retirement.

## Heuristics are not an implementation footnote

For many enterprise problems, a feasible solution inside a strict time budget is more valuable than
an unavailable proof of optimality. The contract must still expose what was sacrificed:

```text
heuristic contract =
    problem class and representation
  + construction/neighborhood/move operators
  + feasibility preservation or repair
  + acceptance and diversification policy
  + randomness and seed
  + termination/resource budget
  + incumbent and bound information, if any
  + quality/robustness benchmark
  + deterministic replay posture
  + failure and no-solution semantics
```

“Heuristic” must never silently mean “correct enough.” A compiler needs typed guarantees such as
exact-optimal, bounded-approximation, feasible-unbounded-quality, best-known-at-budget, infeasible,
unbounded, timeout-with-incumbent, timeout-without-incumbent and solver-failure.

## Company evidence is a separate graph

MathCo is useful evidence for the **solution-company pattern**: custom data products, reusable modules,
cross-industry verticals, data engineering, algorithms and outcome delivery. Its current public material
also emphasizes AI heavily, so it cannot be used as the neutral definition of OR or analytics. The
company graph should separately classify:

```text
company -> claimed practices -> evidenced projects/products -> industries -> source/data needs
        -> delivery model -> reusable IP -> implementation/runtime dependencies -> evidence confidence
```

The company record must not create an analytical type merely because the firm markets a named
offering. Conversely, the practice registry must not omit OR, heuristics or decision science merely
because a vendor packages them under “AI.”

Primary anchors:

- [INFORMS: Operations Research and Analytics](https://www.informs.org/Explore/Operations-Research-Analytics)
- [INFORMS: O.R. Methodologies](https://www.informs.org/Explore/History-of-O.R.-Excellence/O.R.-Methodologies)
- [Google OR-Tools reference](https://or-tools.github.io/docs/)
- [OR-Tools routing search strategy source](https://or-tools.github.io/docs/cpp/routing__enums_8proto_source.html)
- [MathCo company overview](https://mathco.com/our-company/)

