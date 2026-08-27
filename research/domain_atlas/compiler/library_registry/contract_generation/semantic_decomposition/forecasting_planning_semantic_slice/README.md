# Forecasting and integrated-planning semantic slice

This deterministic research slice decomposes forecasting and planning without collapsing them.

```text
observations/vintages -> forecast definition -> run/edition -> evaluation/selection
                                  |                  |
                                  +-> reconciliation +-> governed publication/override

forecasts + assumptions + objectives + constraints + resources
                                  |
                                  v
scenario -> plan alternatives -> feasibility -> cross-functional reconciliation
         -> consensus/approval -> commitment handoff -> variance/replan
```

Forecasting estimates uncertain future observations at an exact origin, horizon and information
cut. Planning coordinates intended choices under goals, constraints, resources and authority. A
scenario is not a forecast; coherence is not accuracy or plan consensus; an approved plan is not
an execution effect.

The slice retains both `product.forecasting_workbench` and
`product.integrated_planning_workbench` as separate unratified product boundaries. The latter is
supported by an ASCM professional definition and independently replaceable SAP, Oracle and Pigment
planning lifecycles; this is product-boundary evidence, not implementation qualification. Financial,
demand, supply, capacity, inventory, workforce and project planning remain vertical solution-pack
profiles over shared horizontal planning mechanics unless later evidence proves independent
product lifecycles.

The planning product is decomposed into 13 exact abstract library contracts. All 13 remain explicit
compiler implementation vacancies; no vendor workflow or generic optimization library is treated as
a silent implementation of them.

All findings are researched candidates. No semantic owner has ratified them, no exact contract or
provider has been selected, no implementation is qualified, and no canonical gap is closed.

Rebuild and validate:

```bash
python3 build_forecasting_planning_semantic_slice.py
python3 validate.py
```
