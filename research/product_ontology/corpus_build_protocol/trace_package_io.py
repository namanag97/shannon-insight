#!/usr/bin/env python3
"""Observe repository-local file I/O for one Python builder in an isolated worktree.

This is evidence for a package-contract candidate, not permission to execute the
builder in the canonical checkout.  Use only in a disposable clean worktree.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import runpy
import sys
from pathlib import Path

ROOT = Path.cwd().resolve()
EVENTS: list[dict] = []


def classify(mode, flags) -> str:
    if isinstance(mode, str):
        if any(char in mode for char in "wax+"):
            return "write"
        return "read"
    if isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
        return "write"
    return "read"


def audit(event, args) -> None:
    if event != "open" or not args:
        return
    try:
        path = Path(os.fspath(args[0]))
    except (TypeError, ValueError):
        return
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    else:
        path = path.resolve()
    try:
        rel = path.relative_to(ROOT).as_posix()
    except ValueError:
        return
    mode = args[1] if len(args) > 1 else None
    flags = args[2] if len(args) > 2 else None
    EVENTS.append({"path": rel, "access": classify(mode, flags)})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("builder")
    parser.add_argument("--package-root", required=True)
    args = parser.parse_args()
    builder = (ROOT / args.builder).resolve()
    package_root = (ROOT / args.package_root).resolve()
    if not builder.is_file() or not package_root.is_dir() or package_root not in builder.parents:
        raise SystemExit("builder must exist inside the declared package root")
    sys.path.insert(0, str(builder.parent))
    sys.addaudithook(audit)
    captured = io.StringIO()
    exit_code = 0
    try:
        with contextlib.redirect_stdout(captured), contextlib.redirect_stderr(captured):
            runpy.run_path(str(builder), run_name="__main__")
    except SystemExit as exc:
        exit_code = int(exc.code or 0)
    unique = sorted({(row["path"], row["access"]) for row in EVENTS})
    reads = [path for path, access in unique if access == "read" and path != args.builder]
    writes = [path for path, access in unique if access == "write"]
    outside_writes = [path for path in writes if not (ROOT / path).is_relative_to(package_root)]
    print(json.dumps({
        "record_kind": "ephemeral_package_io_observation",
        "builder": args.builder,
        "package_root": args.package_root,
        "exit_code": exit_code,
        "repository_read_paths": reads,
        "repository_write_paths": writes,
        "outside_package_write_paths": outside_writes,
        "captured_builder_output": captured.getvalue().strip(),
        "authority_claim": False,
        "determinism_claim": False,
    }, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

