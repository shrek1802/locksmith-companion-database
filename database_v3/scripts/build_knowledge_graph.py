#!/usr/bin/env python3
"""Build compact reverse indexes for the Locksmith Knowledge Engine."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS_DIR = ROOT / "components"
VEHICLES_DIR = ROOT / "vehicles"
EVENTS_DIR = ROOT / "workshop_events"
OUTPUT = ROOT / "compiled" / "knowledge_graph_index.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected object in {path}")
    return value


def add(index: dict[str, set[str]], key: str | None, value: str | None) -> None:
    if key and value:
        index[key].add(value)


def sorted_index(index: dict[str, set[str]]) -> dict[str, list[str]]:
    return {key: sorted(values) for key, values in sorted(index.items())}


def main() -> None:
    components: dict[str, dict[str, Any]] = {}
    vehicles: dict[str, dict[str, Any]] = {}
    events: dict[str, dict[str, Any]] = {}

    for path in sorted(COMPONENTS_DIR.rglob("*.json")):
        component = load_json(path)
        components[component["id"]] = component

    for path in sorted(VEHICLES_DIR.rglob("*.json")):
        vehicle = load_json(path)
        vehicles[vehicle["id"]] = vehicle

    if EVENTS_DIR.exists():
        for path in sorted(EVENTS_DIR.rglob("*.json")):
            if path.name.endswith("template.json"):
                continue
            event = load_json(path)
            if event.get("event_id"):
                events[event["event_id"]] = event

    component_to_vehicles: dict[str, set[str]] = defaultdict(set)
    vehicle_to_components: dict[str, set[str]] = defaultdict(set)
    component_type_to_components: dict[str, set[str]] = defaultdict(set)
    platform_to_vehicles: dict[str, set[str]] = defaultdict(set)
    immobiliser_to_vehicles: dict[str, set[str]] = defaultdict(set)
    transponder_to_vehicles: dict[str, set[str]] = defaultdict(set)
    blade_to_vehicles: dict[str, set[str]] = defaultdict(set)
    procedure_to_vehicles: dict[str, set[str]] = defaultdict(set)
    tool_coverage_to_vehicles: dict[str, set[str]] = defaultdict(set)
    component_to_events: dict[str, set[str]] = defaultdict(set)
    vehicle_to_events: dict[str, set[str]] = defaultdict(set)
    job_type_to_events: dict[str, set[str]] = defaultdict(set)
    tool_to_events: dict[str, set[str]] = defaultdict(set)

    for component_id, component in components.items():
        add(component_type_to_components, component.get("component_type"), component_id)

    for vehicle_id, vehicle in vehicles.items():
        refs = vehicle.get("references", {})
        for ref_type, component_id in refs.items():
            add(component_to_vehicles, component_id, vehicle_id)
            add(vehicle_to_components, vehicle_id, component_id)
            if ref_type == "platform":
                add(platform_to_vehicles, component_id, vehicle_id)
            elif ref_type == "immobiliser":
                add(immobiliser_to_vehicles, component_id, vehicle_id)
            elif ref_type == "transponder":
                add(transponder_to_vehicles, component_id, vehicle_id)
            elif ref_type == "blade":
                add(blade_to_vehicles, component_id, vehicle_id)
            elif ref_type == "procedure":
                add(procedure_to_vehicles, component_id, vehicle_id)
            elif ref_type == "tool_coverage":
                add(tool_coverage_to_vehicles, component_id, vehicle_id)

    for event_id, event in events.items():
        vehicle_record_id = event.get("vehicle_record_id")
        add(vehicle_to_events, vehicle_record_id, event_id)
        add(job_type_to_events, event.get("job_type"), event_id)

        tool = event.get("tool", {})
        tool_key = "::".join(
            part for part in [tool.get("manufacturer"), tool.get("model")] if part
        )
        add(tool_to_events, tool_key or None, event_id)

        component_ids = event.get("component_ids") or event.get("components") or []
        for component_id in component_ids:
            add(component_to_events, component_id, event_id)

    graph = {
        "schema_version": 1,
        "scope": "UK_RHD",
        "counts": {
            "components": len(components),
            "vehicles": len(vehicles),
            "workshop_events": len(events),
        },
        "indexes": {
            "component_to_vehicles": sorted_index(component_to_vehicles),
            "vehicle_to_components": sorted_index(vehicle_to_components),
            "component_type_to_components": sorted_index(component_type_to_components),
            "platform_to_vehicles": sorted_index(platform_to_vehicles),
            "immobiliser_to_vehicles": sorted_index(immobiliser_to_vehicles),
            "transponder_to_vehicles": sorted_index(transponder_to_vehicles),
            "blade_to_vehicles": sorted_index(blade_to_vehicles),
            "procedure_to_vehicles": sorted_index(procedure_to_vehicles),
            "tool_coverage_to_vehicles": sorted_index(tool_coverage_to_vehicles),
            "component_to_workshop_events": sorted_index(component_to_events),
            "vehicle_to_workshop_events": sorted_index(vehicle_to_events),
            "job_type_to_workshop_events": sorted_index(job_type_to_events),
            "tool_to_workshop_events": sorted_index(tool_to_events),
        },
        "records": {
            "components": {
                component_id: {
                    "component_type": component.get("component_type"),
                    "verification": component.get("verification", {}),
                    "revision": component.get("revision", {}),
                }
                for component_id, component in sorted(components.items())
            },
            "vehicles": {
                vehicle_id: {
                    "vehicle": vehicle.get("vehicle", {}),
                    "references": vehicle.get("references", {}),
                }
                for vehicle_id, vehicle in sorted(vehicles.items())
            },
            "workshop_events": events,
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Built knowledge graph with {len(components)} components, "
        f"{len(vehicles)} vehicles and {len(events)} workshop events"
    )


if __name__ == "__main__":
    main()
