#!/usr/bin/env python3
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

def load(name):
    return [json.loads(line) for line in (HERE / name).read_text().splitlines() if line.strip()]

experts = load("all-experts-registry.jsonl")
companies = load("all-specialist-companies-registry.jsonl")
assert len(experts) == len({row["aggregate_expert_id"] for row in experts})
assert len(companies) == len({row["aggregate_company_id"] for row in companies})
assert all(row["source_records"] and row["completeness_claim"] is False for row in experts)
assert all(row["source_records"] and row["completeness_claim"] is False for row in companies)
assert len(experts) >= 350
assert len(companies) >= 75
print(f"PASS: {len(experts)} unique experts and {len(companies)} specialist company/project records")
