# Horizontal evidence identity and claim governance

This package converts three previously qualitative hardening debts into exact, recomputable ledgers:

1. canonical entity identity and relationship debt (`HR03`);
2. source-to-bounded-claim locator debt (`HR04`); and
3. controlled evidence-role debt (`HR05`).

It consumes the existing 38-family shards. It is not a second product registry and does not change a
family's ontology disposition. The generated entity registry deliberately uses
`PROVISIONAL_INTERNAL_HANDLE` and `UNRESOLVED` canonical kinds until authoritative identity evidence
exists. Likewise, organization-family rows are adoption claims only, and research roles are proposed
and unratified. Generating a ledger exposes debt. It does not perform the missing research or close any downstream gate.

## Sovereign boundary

The package owns evidence entities, bounded claims, locators, evidence-role assignments and gate
state. It does not own product semantics, provider implementations, semantic ratification,
implementation qualification or executed acceptance.

Key non-collapse laws include:

```text
legal entity != brand != product != project != foundation
source URL != exact claim locator
adoption evidence != semantic authority
proposed role != ratified role
semantic ratification != implementation qualification != executed acceptance
```

`policy.json`, `evidence-role-taxonomy.json` and `entity-identity-taxonomy.json` are normative only for
this research-corpus governance package. The five source cards bind each imported standard or
registry to narrow claims and state what it cannot establish.

## Generated ledgers

`../build_evidence_governance.py` derives seven files from `manifest.json` and all declared family shards:

- `entity-registry.jsonl`;
- `identity-gaps.jsonl`;
- `organization-membership-claims.jsonl`;
- `research-source-registry.jsonl`;
- `research-membership-claims.jsonl`;
- `frontier.jsonl`; and
- `summary.json`.

The bootstrap workflow commits these ledgers together with regenerated corpus routing on the research
branch. The steady-state workflow then uses exact byte comparison so source drift cannot leave stale counts
or debt projections behind.

## Validation

From the repository root:

```bash
python3 research/analytics_landscape/product_families/build_evidence_governance.py \
  --output /tmp/horizontal-evidence-governance
python3 research/analytics_landscape/product_families/validate_evidence_governance.py \
  --generated /tmp/horizontal-evidence-governance
python3 research/analytics_landscape/product_families/validate.py
```

Once `generated/` is committed:

```bash
python3 research/analytics_landscape/product_families/build_evidence_governance.py --check
python3 research/analytics_landscape/product_families/validate_evidence_governance.py \
  --check-committed
```

A pass proves deterministic coverage and non-overclaim laws encoded by these validators. It does not
prove that provisional identities are resolved, locators are exact, roles are ratified, or any
implementation or vertical has executed.
