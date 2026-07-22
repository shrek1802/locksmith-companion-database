#!/usr/bin/env python3
"""Lightweight integrity checks for Database V3 without external dependencies."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    component_ids = set()
    component_types = {}
    errors = []
    for path in (ROOT / "components").rglob("*.json"):
        item = load(path)
        item_id = item.get("id")
        if not item_id:
            errors.append(f"Missing component id: {path}")
            continue
        if item_id in component_ids:
            errors.append(f"Duplicate component id: {item_id}")
        component_ids.add(item_id)
        component_types[item_id] = item.get("component_type")
    required_refs = {"platform", "immobiliser", "key_system", "blade", "transponder", "procedure", "tool_coverage", "locations"}
    vehicle_ids = set()
    for path in (ROOT / "vehicles").rglob("*.json"):
        item = load(path)
        vehicle_id = item.get("id")
        if vehicle_id in vehicle_ids:
            errors.append(f"Duplicate vehicle id: {vehicle_id}")
        vehicle_ids.add(vehicle_id)
        refs = item.get("references", {})
        missing = required_refs - refs.keys()
        if missing:
            errors.append(f"{vehicle_id}: missing references {sorted(missing)}")
        for ref_type, component_id in refs.items():
            if component_id not in component_ids:
                errors.append(f"{vehicle_id}: missing component {component_id}")
            elif component_types[component_id] != ref_type:
                errors.append(f"{vehicle_id}: {component_id} type mismatch")
        vehicle = item.get("vehicle", {})
        if vehicle.get("market") != "UK" or vehicle.get("steering") != "RHD":
            errors.append(f"{vehicle_id}: must be UK/RHD")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {len(component_ids)} components and {len(vehicle_ids)} vehicles")


if __name__ == "__main__":
    main()
