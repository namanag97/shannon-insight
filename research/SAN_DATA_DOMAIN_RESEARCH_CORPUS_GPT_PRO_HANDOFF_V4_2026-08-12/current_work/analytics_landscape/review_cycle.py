"""Run auditable recurring reviews for the analytics landscape catalogue."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
DEFAULT_CATALOG = ROOT / "analytics_knowledge_base.json"
DEFAULT_RUNS = ROOT / "runs"


def load_catalog(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def domain_coverage(data: dict[str, Any]) -> dict[str, dict[str, int]]:
    type_domains = {item["id"]: item["domain_id"] for item in data["analytics_types"]}
    counts: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"analytics_types": set(), "companies": set(), "experts": set(), "innovations": set()}
    )
    for type_id, domain_id in type_domains.items():
        counts[domain_id]["analytics_types"].add(type_id)
    for collection in ("companies", "experts", "innovations"):
        for item in data[collection]:
            for type_id in item["analytics_type_ids"]:
                counts[type_domains[type_id]][collection].add(item["id"])
    return {
        domain_id: {key: len(values) for key, values in metrics.items()}
        for domain_id, metrics in counts.items()
    }


def ranked_domains(data: dict[str, Any], today: date) -> list[dict[str, Any]]:
    coverage = domain_coverage(data)
    priorities = {item["domain_id"]: item["priority"] for item in data["review"]["queue"]}
    deep_days = int(data["review"]["cadence"]["deep_days"])
    ranked = []
    for domain in data["domains"]:
        reviewed = date.fromisoformat(domain["last_reviewed"]) if domain["last_reviewed"] else None
        days_since = (today - reviewed).days if reviewed else None
        overdue = days_since is None or days_since >= deep_days
        metrics = coverage.get(
            domain["id"],
            {"analytics_types": 0, "companies": 0, "experts": 0, "innovations": 0},
        )
        gaps = max(0, 5 - metrics["companies"]) + max(0, 5 - metrics["experts"])
        innovation_gap = int(metrics["innovations"] == 0)
        queue_priority = priorities.get(domain["id"], 99)
        score = (
            (1000 if reviewed is None else 0)
            + (500 if overdue else 0)
            + gaps * 25
            + innovation_gap * 40
            + max(0, 100 - queue_priority)
        )
        ranked.append(
            {
                "domain_id": domain["id"],
                "name": domain["name"],
                "coverage_status": domain["coverage_status"],
                "last_reviewed": domain["last_reviewed"],
                "days_since_review": days_since,
                "overdue": overdue,
                "coverage": metrics,
                "selection_score": score,
            }
        )
    return sorted(ranked, key=lambda item: (-item["selection_score"], item["domain_id"]))


def command_status(data: dict[str, Any], today: date) -> None:
    print(json.dumps(ranked_domains(data, today), indent=2, ensure_ascii=False))


def command_start(data: dict[str, Any], args: argparse.Namespace, today: date) -> None:
    ranked = ranked_domains(data, today)
    domain_id = args.domain or ranked[0]["domain_id"]
    domain = next((item for item in data["domains"] if item["id"] == domain_id), None)
    if domain is None:
        raise SystemExit(f"unknown domain: {domain_id}")
    run_id = f"review_{today.isoformat()}_{domain_id.removeprefix('dom_')}"
    output = args.output or (DEFAULT_RUNS / f"{run_id}.json")
    output = Path(output)
    if output.exists():
        raise SystemExit(f"review run already exists: {output}")
    manifest = {
        "run_id": run_id,
        "domain_id": domain_id,
        "domain_name": domain["name"],
        "kind": args.kind,
        "status": "in_progress",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "reviewer": None,
        "coverage_at_start": domain_coverage(data).get(domain_id, {}),
        "checklist": [
            {"id": "authoritative_sources", "complete": False, "evidence": []},
            {"id": "company_scope_and_ownership", "complete": False, "evidence": []},
            {"id": "academic_experts", "complete": False, "evidence": []},
            {"id": "practitioner_experts", "complete": False, "evidence": []},
            {"id": "innovations_and_prior_art", "complete": False, "evidence": []},
            {"id": "disconfirming_evidence", "complete": False, "evidence": []},
            {"id": "known_gaps_and_boundaries", "complete": False, "evidence": []},
            {"id": "catalog_validation", "complete": False, "evidence": []}
        ],
        "notes": ""
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(output)


def command_complete(data: dict[str, Any], catalog_path: Path, args: argparse.Namespace) -> None:
    run_path = Path(args.run)
    run = json.loads(run_path.read_text(encoding="utf-8"))
    if run["status"] != "in_progress":
        raise SystemExit(f"run is not in progress: {run['status']}")
    incomplete = [item["id"] for item in run["checklist"] if not item["complete"]]
    if incomplete:
        raise SystemExit(f"review checklist is incomplete: {', '.join(incomplete)}")
    if not run.get("notes", "").strip():
        raise SystemExit("review notes are required")
    coverage = domain_coverage(data).get(run["domain_id"], {})
    if args.mark_reviewed and (coverage.get("companies", 0) < 5 or coverage.get("experts", 0) < 5):
        raise SystemExit(f"reviewed coverage gate failed: {coverage}")

    completed_at = datetime.now(timezone.utc)
    run["status"] = "completed"
    run["completed_at"] = completed_at.isoformat()
    run["reviewer"] = args.reviewer
    run["coverage_at_completion"] = coverage
    run_path.write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    domain = next(item for item in data["domains"] if item["id"] == run["domain_id"])
    domain["last_reviewed"] = completed_at.date().isoformat()
    domain["coverage_status"] = "reviewed" if args.mark_reviewed else "seeded"
    history = data["review"].setdefault("history", [])
    history.append(
        {
            "run_id": run["run_id"],
            "domain_id": run["domain_id"],
            "kind": run["kind"],
            "completed_at": run["completed_at"],
            "reviewer": args.reviewer,
            "result": domain["coverage_status"],
            "manifest": str(run_path.relative_to(ROOT)) if run_path.is_relative_to(ROOT) else str(run_path),
        }
    )
    data["metadata"]["as_of"] = completed_at.date().isoformat()
    data["review"]["last_run"] = history[-1]
    deep_days = int(data["review"]["cadence"]["deep_days"])
    data["review"]["next_deep_review"] = (
        completed_at.date() + timedelta(days=deep_days)
    ).isoformat()
    catalog_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"completed {run['run_id']} as {domain['coverage_status']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")
    start = subparsers.add_parser("start")
    start.add_argument("--domain")
    start.add_argument("--kind", choices=("light", "deep"), default="deep")
    start.add_argument("--output", type=Path)
    complete = subparsers.add_parser("complete")
    complete.add_argument("--run", type=Path, required=True)
    complete.add_argument("--reviewer", required=True)
    complete.add_argument("--mark-reviewed", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = load_catalog(args.catalog)
    today = date.today()
    if args.command == "status":
        command_status(data, today)
    elif args.command == "start":
        command_start(data, args, today)
    elif args.command == "complete":
        command_complete(data, args.catalog, args)


if __name__ == "__main__":
    main()
