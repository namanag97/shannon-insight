"""Validate horizontal machines, vertical packs, and executable composition wiring."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def duplicates(values: list[str]) -> list[str]:
    return sorted(key for key, count in Counter(values).items() if count > 1)


def split_endpoint(value: str) -> tuple[str, str]:
    if "." not in value:
        raise ValueError(f"invalid endpoint {value!r}; expected node.port")
    return tuple(value.rsplit(".", 1))  # type: ignore[return-value]


def asset_ids(pack: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for group in pack["assets"].values():
        result.update(item["id"] for item in group)
    result.update(item["id"] for item in pack["data_contracts"])
    return result


def main() -> None:
    errors: list[str] = []
    registry = read(ROOT / "horizontal_registry.json")
    packs = [read(path) for path in sorted((ROOT / "domain_packs").glob("*.json"))]
    catalog = read(ROOT / "platform_examples.json")
    coverage_map = read(ROOT / "analytics_type_machine_map.json")
    knowledge_base = read(ROOT.parent / "analytics_knowledge_base.json")

    machines = {item["id"]: item for item in registry["machines"]}
    if dupes := duplicates([item["id"] for item in registry["machines"]]):
        errors.append(f"duplicate machines: {dupes}")
    for machine in machines.values():
        for dependency in machine["requires"]:
            if dependency not in machines:
                errors.append(f"{machine['id']} has unknown dependency {dependency}")
        for direction in ("inputs", "outputs"):
            if dupes := duplicates([port["name"] for port in machine[direction]]):
                errors.append(f"{machine['id']} has duplicate {direction}: {dupes}")
            for port in machine[direction]:
                if port["type"] not in registry["canonical_types"]:
                    errors.append(f"{machine['id']}.{port['name']} uses unknown type {port['type']}")

    library_members = [machine_id for library in registry["libraries"] for machine_id in library["machines"]]
    for machine_id in library_members:
        if machine_id not in machines:
            errors.append(f"library contains unknown machine {machine_id}")
    if dupes := duplicates(library_members):
        errors.append(f"machines owned by multiple libraries: {dupes}")
    unowned = sorted(set(machines) - set(library_members))
    if unowned:
        errors.append(f"machines without library ownership: {unowned}")

    known_types = {item["id"] for item in knowledge_base["analytics_types"]}
    mapped_types = [item["analytics_type_id"] for item in coverage_map["mappings"]]
    if dupes := duplicates(mapped_types):
        errors.append(f"analytics types mapped more than once: {dupes}")
    if missing_types := sorted(known_types - set(mapped_types)):
        errors.append(f"analytics types without machine mapping: {missing_types}")
    if unknown_types := sorted(set(mapped_types) - known_types):
        errors.append(f"machine map contains unknown analytics types: {unknown_types}")
    for mapping in coverage_map["mappings"]:
        unknown_machines = sorted(set(mapping["machine_ids"]) - set(machines))
        if unknown_machines:
            errors.append(f"{mapping['analytics_type_id']} maps unknown machines: {unknown_machines}")
        if mapping["status"] == "covered" and mapping["missing"]:
            errors.append(f"{mapping['analytics_type_id']} is covered but has missing primitives")
        if mapping["status"] != "covered" and not mapping["missing"]:
            errors.append(f"{mapping['analytics_type_id']} is {mapping['status']} without named gaps")

    pack_by_id = {pack["id"]: pack for pack in packs}
    if dupes := duplicates([pack["id"] for pack in packs]):
        errors.append(f"duplicate domain packs: {dupes}")
    for pack in packs:
        known_assets = asset_ids(pack)
        for binding in pack["machine_bindings"]:
            machine = machines.get(binding["machine_id"])
            if machine is None:
                errors.append(f"{pack['id']} binds unknown machine {binding['machine_id']}")
                continue
            unknown_config = sorted(set(binding["config"]) - set(machine["config"]))
            if unknown_config:
                errors.append(f"{pack['id']} configures unsupported keys on {machine['id']}: {unknown_config}")
            for key, value in binding["config"].items():
                if key.endswith("_ref") and isinstance(value, str):
                    base = value.removesuffix(".*")
                    if value not in known_assets and not any(item.startswith(base + ".") for item in known_assets):
                        errors.append(f"{pack['id']} binding reference not found: {value}")

    # A vocabulary leak is the fastest signal that an allegedly horizontal library became vertical.
    allowed_generic = {"asset", "event", "quantity", "location", "interval", "currency", "duration", "state", "action"}
    forbidden: set[str] = set()
    for pack in packs:
        for values in pack["vocabulary"].values():
            forbidden.update(value.lower() for value in values)
        for role, values in pack["canonical_role_bindings"].items():
            if role in {"asset", "event", "location"}:
                forbidden.update(value.lower() for value in values)
    forbidden -= allowed_generic
    horizontal_text = json.dumps(registry["machines"], ensure_ascii=False).lower()
    leaked = sorted(term for term in forbidden if re.search(rf"\b{re.escape(term)}\b", horizontal_text))
    if leaked:
        errors.append(f"vertical vocabulary leaked into horizontal machines: {leaked}")

    for composition in catalog["compositions"]:
        if composition["domain_pack_id"] not in pack_by_id:
            errors.append(f"{composition['id']} has unknown domain pack")
        nodes = {node["id"]: node["machine_id"] for node in composition["nodes"]}
        if dupes := duplicates([node["id"] for node in composition["nodes"]]):
            errors.append(f"{composition['id']} has duplicate nodes: {dupes}")
        for node_id, machine_id in nodes.items():
            if machine_id not in machines:
                errors.append(f"{composition['id']}.{node_id} has unknown machine {machine_id}")
        graph: dict[str, set[str]] = defaultdict(set)
        indegree = {node_id: 0 for node_id in nodes}
        for edge in composition["edges"]:
            try:
                from_node, from_port = split_endpoint(edge["from"])
                to_node, to_port = split_endpoint(edge["to"])
            except ValueError as exc:
                errors.append(f"{composition['id']}: {exc}")
                continue
            if from_node not in nodes or to_node not in nodes:
                errors.append(f"{composition['id']} edge has unknown node: {edge}")
                continue
            source = machines[nodes[from_node]]
            target = machines[nodes[to_node]]
            source_types = {port["name"]: port["type"] for port in source["outputs"]}
            target_types = {port["name"]: port["type"] for port in target["inputs"]}
            if from_port not in source_types or to_port not in target_types:
                errors.append(f"{composition['id']} edge has unknown or wrong-direction port: {edge}")
            elif source_types[from_port] != target_types[to_port]:
                errors.append(f"{composition['id']} type mismatch {edge}: {source_types[from_port]} != {target_types[to_port]}")
            if to_node not in graph[from_node]:
                graph[from_node].add(to_node)
                indegree[to_node] += 1
        queue = deque(node for node, degree in indegree.items() if degree == 0)
        visited = 0
        while queue:
            node = queue.popleft()
            visited += 1
            for successor in graph[node]:
                indegree[successor] -= 1
                if indegree[successor] == 0:
                    queue.append(successor)
        if visited != len(nodes):
            errors.append(f"{composition['id']} wiring contains a cycle")
        for machine_id in set(nodes.values()):
            selected = set(nodes.values())
            missing = sorted(set(machines[machine_id]["requires"]) - selected)
            if missing:
                errors.append(f"{composition['id']} selects {machine_id} without dependencies {missing}")

    if errors:
        print(json.dumps({"valid": False, "errors": errors}, indent=2))
        raise SystemExit(1)
    print(json.dumps({
        "valid": True,
        "libraries": len(registry["libraries"]),
        "machines": len(machines),
        "domain_packs": len(packs),
        "compositions": len(catalog["compositions"]),
        "analytics_type_coverage": dict(Counter(item["status"] for item in coverage_map["mappings"])),
        "known_horizontal_gaps": registry["coverage"]["known_gaps"]
    }, indent=2))


if __name__ == "__main__":
    main()
