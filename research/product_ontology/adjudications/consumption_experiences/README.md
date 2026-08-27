# Analytical consumption and experience product adjudication

Status: evidence-backed adjudicated candidate, not ratified products or qualified providers.

This slice resolves an overloaded product family:

```text
analytical consumption pattern
          |
          v
analytics experience suite ---------------------- packaging only
          |
          +--> BI and reporting experience ------- strong product candidate
          +--> embedded analytics delivery -------- presumptive product
          `--> analytical notebook environment ---- presumptive product

visual grammar/compiler/renderer ----------------- library + runtime offer
dashboard widget --------------------------------- presentation artifact
analytical alert/subscription -------------------- split capabilities + delivery neighbor
spreadsheet governance --------------------------- semantic/library contract; product deferred
```

The product boundaries import semantic metrics, query execution, identity/policy and notification
delivery. They do not re-own those meanings. Report, dashboard, widget, snapshot, notebook document,
kernel session, embedded guest grant, alert state and delivery receipt remain different identities.

Thirteen product-facing library contracts map exactly to existing compiler-library candidates
in `library.cbv.*` and carry explicit BI, embedded-analytics or notebook `product_refs`. The
BI/reporting, embedded-analytics and notebook products now each have a complete candidate 29-field
strategic/tactical DDD dossier. Report authoring is an explicit lifecycle-owned library instead of
an accidental rendering behavior. Notebook kernel execution remains an imported runtime capability,
not an uncovered notebook-owned contract. Exact internally owned requirements are fully covered;
all implementation offers remain unqualified and all product requirements remain unbound. Passing
this corpus cannot qualify Power BI, Superset, Jupyter, Vega, Observable, Alertmanager, Grafana or
any deployment occurrence.

Model and tool-agent assistance is optional. It may propose a chart, narrative, notebook step,
alert rule or explanation, but deterministic owners still validate semantics, authority,
accessibility, disclosure, execution and evidence. Removing the extension leaves all core product
contracts intact.

Rebuild and validate from the repository root:

```bash
python3 research/product_ontology/adjudications/consumption_experiences/build_bundle.py
python3 research/product_ontology/adjudications/consumption_experiences/validate.py
python3 research/product_ontology/adjudications/consumption_experiences/build_bundle.py --check
```
