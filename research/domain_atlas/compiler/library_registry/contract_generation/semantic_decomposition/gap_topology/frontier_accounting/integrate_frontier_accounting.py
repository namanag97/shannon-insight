#!/usr/bin/env python3
"""Install the frontier-accounting validator into the repository-wide validation chain."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[7]
GLOBAL_VALIDATOR = REPO_ROOT / "research/product_ontology/validate_registry.py"
PARENT_README = HERE.parent / "README.md"

VALIDATION_SENTINEL = "semantic_gap_frontier_accounting_validator ="
VALIDATION_BLOCK = r"""
    semantic_gap_frontier_accounting_validator = (
        ROOT.parent
        / "domain_atlas/compiler/library_registry/contract_generation/semantic_decomposition/"
        "gap_topology/frontier_accounting/validate.py"
    )
    if not semantic_gap_frontier_accounting_validator.is_file():
        errors.append("semantic gap-frontier accounting validator is missing")
    else:
        completed = subprocess.run(
            [sys.executable, str(semantic_gap_frontier_accounting_validator)],
            cwd=ROOT.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        output = completed.stdout.strip()
        if completed.returncode != 0:
            errors.append(
                "semantic gap-frontier accounting failed: "
                + (output or completed.stderr.strip())
            )
        elif output:
            adjudication_outputs.append(output)
"""

README_SENTINEL = "> **Live-count authority:**"
README_NOTICE = """\
> **Live-count authority:** Numeric snapshots in the narrative below are historical context.
> `summary.json` is authoritative for the current cluster/atom frontier, and
> `frontier_accounting/summary.json` plus its validator prove exact cluster-to-atom-to-kernel
> routing. Neither file claims semantic closure, implementation, qualification or acceptance.

"""


def main() -> int:
    text = GLOBAL_VALIDATOR.read_text(encoding="utf-8")
    if VALIDATION_SENTINEL not in text:
        marker = "\n    if errors:\n"
        index = text.rfind(marker)
        if index < 0:
            raise ValueError("could not find final error gate in validate_registry.py")
        text = text[:index] + "\n" + VALIDATION_BLOCK.rstrip() + "\n" + text[index:]
        GLOBAL_VALIDATOR.write_text(text, encoding="utf-8")

    readme = PARENT_README.read_text(encoding="utf-8")
    if README_SENTINEL not in readme:
        title = "# Semantic gap topology\n\n"
        if not readme.startswith(title):
            raise ValueError("unexpected gap-topology README heading")
        readme = title + README_NOTICE + readme[len(title):]
        PARENT_README.write_text(readme, encoding="utf-8")

    report = {
        "global_validator_integration": VALIDATION_SENTINEL
        in GLOBAL_VALIDATOR.read_text(encoding="utf-8"),
        "parent_readme_live_count_notice": README_SENTINEL
        in PARENT_README.read_text(encoding="utf-8"),
        "completion_claim": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
