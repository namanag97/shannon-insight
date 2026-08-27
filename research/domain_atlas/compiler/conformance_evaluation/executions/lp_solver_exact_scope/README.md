# Exact-scope continuous-LP provider execution

Status: **executed-test evidence, not independently appraised, not qualified**.

This pilot challenged the earlier assumption that the generic `OR-Tools` and `HiGHS` provider
names were sufficiently precise substitution identities. They are not. The executed subjects are:

```text
OR-Tools suite
  -> GLOP solver
     -> MPSolver Python adapter
        -> ortools 9.15.6755 wheel/native libraries
           -> one isolated macOS arm64 Python 3.14 process occurrence

HiGHS project
  -> HiGHS solver
     -> highspy Python adapter
        -> highspy 1.15.1 wheel/native libraries
           -> one isolated macOS arm64 Python 3.14 process occurrence
```

Neither chain is equivalent to its product/project name, and neither receipt generalizes outside
the exact package bytes, dependency lock, adapter, target, protocol, fixtures and oracle edition.

## What executed

Six deterministic continuous-LP fixtures were run independently through each provider:

- unique optimum;
- degenerate/multiple optimum;
- coefficient-scale separation;
- infeasible model;
- unbounded model; and
- non-finite input refused before provider invocation.

The semantic oracle independently recomputed bounds, constraint satisfaction and objective values.
It compares degenerate models by feasibility and objective, not by variable-vector identity.

## Findings

```text
                                      GLOP/MPSolver       HiGHS/highspy
safe objective/status scope                PASS                PASS
precise infeasible vs unbounded            FAIL                PASS
same-process coexistence with pair         FAIL                FAIL AS A PAIR
independent appraisal                  NOT EXECUTED        NOT EXECUTED
qualified offer                              NO                  NO
portable offer                               NO                  NO
```

The optimal objective values agreed for all three bounded fixtures. HiGHS returned distinct
`Infeasible` and `Unbounded` states. GLOP through MPSolver returned `INFEASIBLE` for both fixtures.
This is not treated as proof that the unbounded fixture is infeasible: the anti-corruption layer
weakens the MPSolver status to `infeasible_or_unbounded`, matching the versioned OR-Tools source
mapping. Consequently the pair agrees only for the weaker safe status contract and is not
substitutable where exact terminal classification is required.

An additional negative twin imported `highspy` and OR-Tools in one Python process. The observed
target failed at native loading because the wheels exposed incompatible `libhighs` symbols. The
target binder must therefore select process isolation for this exact pair and target. This is a
target/cohabitation constraint, not proof that either solver is semantically defective.

## Corpus corrections

1. A provider suite/project is not a bindable offer. Solver, API adapter, version, artifact and
   deployed occurrence require separate identities.
2. Status precision is a compiler decision. `infeasible_or_unbounded` cannot be strengthened to
   `infeasible` merely because an adapter enum lacks the ambiguous state.
3. Provider substitution depends on exact contracts plus target cohabitation, not interface shape.
4. Executed test receipts remain below independent appraisal and exact-scope qualification.
5. Cancellation, progress, certificates, performance, security, licensing and vertical acceptance
   remain untested and therefore unavailable for binding.

## Authoritative artifacts

- `protocol.json` — exact providers, dependencies, fixtures, scope, exclusions, sources and laws.
- `provider_adapter.py` — isolated provider ACLs with explicit status weakening.
- `run_execution.py` — append-only execution orchestrator and receipt generator.
- `validate_execution.py` — digest, semantic, receipt-schema and non-overclaim validator.
- `runs/run-20260826-macos-arm64-python3_14-001/` — retained execution evidence.

Run a new append-only attempt:

```sh
python3 research/domain_atlas/compiler/conformance_evaluation/executions/lp_solver_exact_scope/run_execution.py \
  --run-id <new-unique-run-id>
```

Validate the retained attempt:

```sh
python3 research/domain_atlas/compiler/conformance_evaluation/executions/lp_solver_exact_scope/validate_execution.py \
  research/domain_atlas/compiler/conformance_evaluation/executions/lp_solver_exact_scope/runs/run-20260826-macos-arm64-python3_14-001
```

Passing the validator proves only that the retained evidence is internally consistent with this
candidate protocol. It does not convert the executed receipts into qualification.
