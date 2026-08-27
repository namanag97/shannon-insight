#!/usr/bin/env python3
"""Validate total stage ownership for the bounded Python application pipeline."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


class Failure(RuntimeError):
    pass


def fail(message: str) -> None:
    raise Failure(message)


def load_json(path: Path) -> Any:
    if not path.exists():
        fail(f"missing required file: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    try:
        pipeline = load_json(HERE / "application-pipeline.json")
        rules = load_json(HERE / "module-allocation-rules.json")
        stages = pipeline["stages"]
        if not stages:
            fail("application pipeline has no stages")
        expected_indexes = list(range(1, len(stages) + 1))
        if [stage["stage_index"] for stage in stages] != expected_indexes:
            fail("stage indexes are not total and monotone")
        stage_ids = [stage["stage_id"] for stage in stages]
        if len(stage_ids) != len(set(stage_ids)):
            fail("duplicate stage identity")

        known_modules = set(rules["allocations"])
        known_layers = set(rules["layers"])
        available = set(pipeline["external_inputs"])
        output_owner: dict[str, str] = {}
        for stage in stages:
            if stage["owner_layer"] not in known_layers:
                fail(f"unknown stage owner layer: {stage['stage_id']}")
            unresolved_modules = sorted(set(stage["module_owner_keys"]) - known_modules)
            if unresolved_modules:
                fail(
                    f"stage {stage['stage_id']} references unknown module owners: "
                    f"{unresolved_modules}"
                )
            if not stage["inputs"] or not stage["outputs"]:
                fail(f"stage {stage['stage_id']} lacks inputs or outputs")
            missing_inputs = sorted(set(stage["inputs"]) - available)
            if missing_inputs:
                fail(f"stage {stage['stage_id']} consumes unowned inputs: {missing_inputs}")
            for output in stage["outputs"]:
                if output in output_owner:
                    fail(
                        f"durable output {output} has two owners: "
                        f"{output_owner[output]} and {stage['stage_id']}"
                    )
                output_owner[output] = stage["stage_id"]
                available.add(output)
            if not stage["decisions"] or not stage["refusals"]:
                fail(f"stage {stage['stage_id']} lacks decision/refusal semantics")
            if stage["semantic_authority"] or stage["qualification_claim"]:
                fail(f"stage {stage['stage_id']} promotes authority or qualification")
            if stage["implementation_status"] != "OBSERVED_IMPLEMENTATION_CANDIDATE_UNQUALIFIED":
                fail(f"unsafe stage implementation status: {stage['stage_id']}")

        final_outputs = set(stages[-1]["outputs"])
        if set(pipeline["terminal_outputs"]) != final_outputs:
            fail("terminal outputs are not owned exactly by the final experience stage")
        if any(not output.startswith("experience.") for output in final_outputs):
            fail("final experience stage emits non-experience truth")
        if len(pipeline["pipeline_laws"]) < 10:
            fail("pipeline non-collapse laws are incomplete")
        if pipeline["horizontal_semantic_authority"]:
            fail("application pipeline claims horizontal semantic authority")
        if pipeline["qualified_stage_count"] != 0:
            fail("application pipeline fabricates qualified stages")
        if pipeline["completion_claim"] is not False:
            fail("application pipeline claims completion")
    except (Failure, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL python_application_pipeline: {exc}", file=sys.stderr)
        return 1

    print(
        "PASS python_application_pipeline "
        + json.dumps(
            {
                "stage_count": len(stages),
                "owned_output_count": len(output_owner),
                "qualified_stage_count": pipeline["qualified_stage_count"],
                "completion_claim": pipeline["completion_claim"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
