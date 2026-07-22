#!/usr/bin/env python3
"""Compile Database V3 component references into app-ready JSON."""
from __future__ import annotations

import json
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ROOT / "components"
VEHICLES = ROOT / "vehicles"
WORKSHOP_EVENTS = ROOT / "workshop_events"
OUTPUT = ROOT / "compiled" / "vag_mqb_pilot.json"
REFERENCE_ORDER = ["platform", "immobiliser", "key_system", "blade", "transponder", "procedure", "tool_coverage", "locations"]
STATUS_RANK = {"unverified": 0, "provisional": 1, "source_verified": 2, "workshop_verified": 3}
CONFIDENCE_RANK = {"unknown": 0, "low": 1, "medium": 2, "high": 3}


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


def load_workshop_events() -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    if not WORKSHOP_EVENTS.exists():
        return events
    for path in sorted(WORKSHOP_EVENTS.glob("*.json")):
        if path.name.endswith(".template.json"):
            continue
        event = load_json(path)
        event["_source_file"] = path.name
        events.append(event)
    return events


def event_indexes(events: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], dict[str, list[dict[str, Any]]]]:
    by_component: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_vehicle: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        for component_id in event.get("component_ids", []):
            by_component[component_id].append(event)
        vehicle_record_id = event.get("vehicle_record_id")
        if vehicle_record_id:
            by_vehicle[vehicle_record_id].append(event)
    return dict(by_component), dict(by_vehicle)


def normalise_event(event: dict[str, Any]) -> dict[str, Any]:
    """Convert a standalone event to the compact evidence shape used by compiled records."""
    return {
        "event_id": event.get("event_id"),
        "vehicle_record_id": event.get("vehicle_record_id"),
        "vehicle": deepcopy(event.get("vehicle", {})),
        "job_type": event.get("job_type") or event.get("operation"),
        "operation": event.get("operation"),
        "tool": deepcopy(event.get("tool", {})),
        "adapters": deepcopy(event.get("adapters", [])),
        "result": event.get("result"),
        "completed_at": event.get("completed_at"),
        "notes": event.get("notes"),
        "evidence_scope": event.get("evidence_scope"),
        "component_ids": deepcopy(event.get("component_ids", [])),
        "source": "standalone_workshop_event",
        "source_file": event.get("_source_file"),
    }


def merge_events(inline: list[dict[str, Any]], standalone: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge evidence without duplicating the same event ID."""
    merged: list[dict[str, Any]] = []
    seen: set[str] = set()
    for event in [*inline, *(normalise_event(item) for item in standalone)]:
        event_id = event.get("event_id")
        dedupe_key = event_id or json.dumps(event, sort_keys=True, ensure_ascii=False)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        merged.append(deepcopy(event))
    return merged


def verification_snapshot(component: dict[str, Any], standalone_events: list[dict[str, Any]]) -> dict[str, Any]:
    verification = deepcopy(component.get("verification", {}))
    verification.setdefault("status", "unverified")
    verification.setdefault("confidence", "unknown")
    verification.setdefault("last_checked", None)
    verification.setdefault("sources", [])
    verification["workshop_history"] = merge_events(
        verification.get("workshop_history", []),
        standalone_events,
    )
    return {
        "component_id": component["id"],
        "component_type": component["component_type"],
        "revision": deepcopy(component.get("revision", {"version": 1, "updated_at": None, "change_summary": "Legacy V3 pilot component"})),
        "compatibility": deepcopy(component.get("compatibility", {"applies_to": [], "exclusions": [], "conditions": []})),
        "verification": verification,
    }


def evidence_summary(evidence: list[dict[str, Any]], vehicle_record_id: str) -> dict[str, Any]:
    statuses = [item["verification"]["status"] for item in evidence]
    confidences = [item["verification"]["confidence"] for item in evidence]
    exact_successes = []
    related_successes = []
    seen_exact: set[tuple[str | None, str]] = set()
    seen_related: set[tuple[str | None, str]] = set()

    for item in evidence:
        for event in item["verification"].get("workshop_history", []):
            if event.get("result") != "success":
                continue
            event_vehicle_id = event.get("vehicle_record_id")
            summary = {
                "component_id": item["component_id"],
                "component_type": item["component_type"],
                "event_id": event.get("event_id"),
                "vehicle_record_id": event_vehicle_id,
                "job_type": event.get("job_type") or event.get("operation"),
                "tool": deepcopy(event.get("tool")),
                "completed_at": event.get("completed_at"),
                "evidence_scope": event.get("evidence_scope"),
            }
            dedupe_key = (event.get("event_id"), item["component_id"])
            if event_vehicle_id == vehicle_record_id and event.get("evidence_scope") != "related_platform":
                if dedupe_key not in seen_exact:
                    exact_successes.append(summary)
                    seen_exact.add(dedupe_key)
            else:
                if dedupe_key not in seen_related:
                    related_successes.append(summary)
                    seen_related.add(dedupe_key)

    weakest_status = min(statuses, key=lambda value: STATUS_RANK.get(value, -1))
    weakest_confidence = min(confidences, key=lambda value: CONFIDENCE_RANK.get(value, -1))
    return {
        "display_status": "exact_vehicle_workshop_verified" if exact_successes else "shared_system_evidence" if related_successes else weakest_status,
        "lowest_component_status": weakest_status,
        "lowest_component_confidence": weakest_confidence,
        "exact_vehicle_success_count": len(exact_successes),
        "related_vehicle_success_count": len(related_successes),
        "exact_vehicle_evidence": exact_successes,
        "related_vehicle_evidence": related_successes,
        "warning": None if exact_successes else "No successful workshop event is recorded for this exact vehicle record. Shared component information must not be presented as exact-vehicle verification.",
    }


def compile_vehicle(
    record: dict[str, Any],
    components: dict[str, dict[str, Any]],
    events_by_component: dict[str, list[dict[str, Any]]],
    events_by_vehicle: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    compiled: dict[str, Any] = {"vehicle": deepcopy(record["vehicle"])}
    references = record["references"]
    evidence = []
    for reference_type in REFERENCE_ORDER:
        component_id = references[reference_type]
        component = components.get(component_id)
        if component is None:
            raise KeyError(f"Missing component {component_id} referenced by {record['id']}")
        if component["component_type"] != reference_type:
            raise ValueError(f"{component_id} is {component['component_type']}, expected {reference_type}")
        compiled = deep_merge(compiled, component["data"])
        evidence.append(verification_snapshot(component, events_by_component.get(component_id, [])))

    compiled = deep_merge(compiled, record.get("overrides", {}))
    compiled.setdefault("locksmith_configuration_id", record["id"])
    exact_vehicle_events = [normalise_event(event) for event in events_by_vehicle.get(record["id"], [])]
    compiled["v3_metadata"] = {
        "vehicle_record_id": record["id"],
        "references": references,
        "component_evidence": evidence,
        "vehicle_workshop_events": exact_vehicle_events,
        "verification_summary": evidence_summary(evidence, record["id"]),
        "confidence_rule": "Exact vehicle workshop evidence is distinct from related-platform evidence; no status is promoted during compilation.",
    }
    return compiled


def main() -> None:
    components = component_index()
    events = load_workshop_events()
    events_by_component, events_by_vehicle = event_indexes(events)
    output_records = []
    for path in sorted(VEHICLES.rglob("*.json")):
        output_records.append(
            compile_vehicle(
                load_json(path),
                components,
                events_by_component,
                events_by_vehicle,
            )
        )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output_records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Compiled {len(output_records)} records and injected {len(events)} standalone workshop events into {OUTPUT}")


if __name__ == "__main__":
    main()
