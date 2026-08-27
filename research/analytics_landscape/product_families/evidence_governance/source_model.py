#!/usr/bin/env python3
"""Typed records and deterministic serialization for horizontal evidence governance."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


@dataclass(frozen=True)
class EvidenceLocator:
    source_url: str
    selector_kind: Optional[str]
    selector_value: Optional[str]
    source_state: Optional[str]
    locator_state: str
    exact_claim_support: bool


@dataclass(frozen=True)
class EvidenceRoleAssignment:
    roles: Sequence[str]
    role_state: str
    rationale: str


@dataclass(frozen=True)
class EntityRecord:
    entity_id: str
    display_name: str
    primary_url: str
    source_declared_kind: str
    canonical_entity_kind: str
    identity_state: str
    authoritative_identifiers: Sequence[Dict[str, str]]
    aliases: Sequence[str]
    source_family_ids: Sequence[str]
    semantic_authority: bool
    completion_claim: bool


@dataclass(frozen=True)
class EvidenceClaim:
    claim_id: str
    claim_kind: str
    subject_id: str
    predicate: str
    object_id: str
    statement: str
    family_id: str
    evidence_bindings: Sequence[EvidenceLocator]
    role_assignment: EvidenceRoleAssignment
    claim_state: str
    semantic_authority: bool
    implementation_qualification: bool
    executed_acceptance: bool
    completion_claim: bool


def record(value: Any) -> Dict[str, Any]:
    return asdict(value)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical_json(row) + "\n" for row in rows), encoding="utf-8")


def stable_claim_id(claim_kind: str, family_id: str, source_id: str) -> str:
    material = "\x1f".join((claim_kind, family_id, source_id))
    return "claim_{}_{}".format(claim_kind, sha256_text(material)[:20])
