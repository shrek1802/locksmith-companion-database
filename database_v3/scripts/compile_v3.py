#!/usr/bin/env python3
"""Compile Database V3 component references into app-ready JSON."""
from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "components"
VEHICLES = ROOT / "vehicles"
OUTPUT = ROOT / "compiled" / "vag_mqb_pilot.json"
REFERENCE_ORDER = ["platform", "immobiliser", "key_system", "blade", "transponder", "procedure", "tool_coverage", "locations"]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected object in {path}")
    return value


def deep_merge(base: dict[str, Any], incoming: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in incoming.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def component_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for path in COMPONENTS.rglob("*.json"):
        component = load_json(path)
        component_id = component.get("id")
        if not component_id:
            raise ValueError(f"Component without id: {path}")
        if component_id in index:
            raise ValueError(f"Duplicate component id: {component_id}")
        index[component_id] = component
    return index


def compile_vehicle(record: dict[str, Any], components: dict[str, dict[str, Any]]) -> dict[str, Any]:
    compiled: dict[str, Any] = {"vehicle": deepcopy(record["vehicle"])}
    references = record["references"]
    for reference_type in REFERENCE_ORDER:
        component_id = references[reference_type]
        component = components.get(component_id)
        if component is None:
            raise KeyError(f"Missing component {component_id} referenced by {record['id']}")
        if component["component_type"] != reference_type:
            raise ValueError(f"{component_id} is {component['component_type']}, expected {reference_type}")
        compiled = deep_merge(compiled, component["data"])
    compiled = deep_merge(compiled, record.get("overrides", {}))
    compiled.setdefault("locksmith_configuration_id", record["id"])
    compiled["v3_metadata"] = {"vehicle_record_id": record["id"], "references": references}
    return compiled


def main() -> None:
    components = component_index()
    output_records = []
    for path in sorted(VEHICLES.rglob("*.json")):
        output_records.append(compile_vehicle(load_json(path), components))
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output_records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Compiled {len(output_records)} records to {OUTPUT}")


if __name__ == "__main__":
    main()
