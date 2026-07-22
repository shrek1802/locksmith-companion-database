#!/usr/bin/env python3
"""Integrity and evidence-safety checks for Database V3."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_STATUSES = {"unverified", "provisional", "source_verified", "workshop_verified"}
VALID_CONFIDENCE = {"unknown", "low", "medium", "high"}
VALID_RESULTS = {"success", "partial", "failed", "not_attempted"}
VALID_TYPES = {"platform", "immobiliser", "key_system", "blade", "transponder", "procedure", "tool_coverage", "locations"}
REQUIRED_REFS = VALID_TYPES


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def valid_iso_date(value) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def main() -> None:
    component_ids = set()
    component_types = {}
    components = {}
    errors = []
    warnings = []

    for path in sorted((ROOT / "components").rglob("*.json")):
        item = load(path)
        item_id = item.get("id")
        if not item_id:
            errors.append(f"Missing component id: {path}")
            continue
        if item_id in component_ids:
            errors.append(f"Duplicate component id: {item_id}")
        component_ids.add(item_id)
        component_types[item_id] = item.get("component_type")
        components[item_id] = item

        component_type = item.get("component_type")
        if component_type not in VALID_TYPES:
            errors.append(f"{item_id}: invalid component_type {component_type}")

        revision = item.get("revision")
        if not isinstance(revision, dict):
            errors.append(f"{item_id}: revision block is required")
        else:
            if not isinstance(revision.get("version"), int) or revision["version"] < 1:
                errors.append(f"{item_id}: revision.version must be an integer >= 1")
            if not valid_iso_date(revision.get("updated_at")):
                errors.append(f"{item_id}: revision.updated_at must be an ISO date")
            if not revision.get("change_summary"):
                errors.append(f"{item_id}: revision.change_summary is required")

        compatibility = item.get("compatibility")
        if not isinstance(compatibility, dict):
            errors.append(f"{item_id}: compatibility block is required")
        else:
            for field in ("applies_to", "exclusions", "conditions"):
                if not isinstance(compatibility.get(field), list):
                    errors.append(f"{item_id}: compatibility.{field} must be an array")

        verification = item.get("verification", {})
        status = verification.get("status")
        confidence = verification.get("confidence")
        history = verification.get("workshop_history")
        sources = verification.get("sources")
        if status not in VALID_STATUSES:
            errors.append(f"{item_id}: invalid verification status {status}")
        if confidence not in VALID_CONFIDENCE:
            errors.append(f"{item_id}: invalid confidence {confidence}")
        if not isinstance(history, list):
            errors.append(f"{item_id}: verification.workshop_history must be an array")
            history = []
        if not isinstance(sources, list):
            errors.append(f"{item_id}: verification.sources must be an array")
        if status == "source_verified" and not sources:
            errors.append(f"{item_id}: source_verified requires at least one source")
        if status == "workshop_verified" and not any(event.get("result") == "success" for event in history):
            errors.append(f"{item_id}: workshop_verified requires a successful workshop event")
        if status != "workshop_verified" and any(event.get("result") == "success" for event in history):
            warnings.append(f"{item_id}: successful workshop evidence exists but status is {status}")

        event_ids = set()
        for event in history:
            event_id = event.get("event_id")
            if not event_id:
                errors.append(f"{item_id}: workshop event requires event_id")
            elif event_id in event_ids:
                errors.append(f"{item_id}: duplicate workshop event_id {event_id}")
            event_ids.add(event_id)
            if event.get("result") not in VALID_RESULTS:
                errors.append(f"{item_id}: invalid workshop result {event.get('result')}")
            if not event.get("vehicle_record_id"):
                errors.append(f"{item_id}: workshop event requires vehicle_record_id")
            vehicle = event.get("vehicle", {})
            if vehicle.get("market") != "UK" or vehicle.get("steering") != "RHD":
                errors.append(f"{item_id}: workshop event must identify UK/RHD vehicle")
            tool = event.get("tool", {})
            if not tool.get("manufacturer") or not tool.get("model"):
                errors.append(f"{item_id}: workshop event requires exact tool manufacturer/model")
            if not event.get("job_type"):
                errors.append(f"{item_id}: workshop event requires job_type")
            if not valid_iso_date(event.get("completed_at")):
                errors.append(f"{item_id}: workshop event completed_at must be an ISO date")

    vehicle_ids = set()
    vehicle_records = []
    for path in sorted((ROOT / "vehicles").rglob("*.json")):
        item = load(path)
        vehicle_records.append(item)
        vehicle_id = item.get("id")
        if not vehicle_id:
            errors.append(f"Missing vehicle id: {path}")
            continue
        if vehicle_id in vehicle_ids:
            errors.append(f"Duplicate vehicle id: {vehicle_id}")
        vehicle_ids.add(vehicle_id)
        refs = item.get("references", {})
        missing = REQUIRED_REFS - refs.keys()
        extra = refs.keys() - REQUIRED_REFS
        if missing:
            errors.append(f"{vehicle_id}: missing references {sorted(missing)}")
        if extra:
            errors.append(f"{vehicle_id}: unknown references {sorted(extra)}")
        for ref_type, component_id in refs.items():
            if component_id not in component_ids:
                errors.append(f"{vehicle_id}: missing component {component_id}")
            elif component_types[component_id] != ref_type:
                errors.append(f"{vehicle_id}: {component_id} type mismatch")
        vehicle = item.get("vehicle", {})
        if vehicle.get("market") != "UK" or vehicle.get("steering") != "RHD":
            errors.append(f"{vehicle_id}: must be UK/RHD")
        if not isinstance(item.get("overrides"), dict):
            errors.append(f"{vehicle_id}: overrides must be an object")

    for component_id, component in components.items():
        for event in component.get("verification", {}).get("workshop_history", []):
            event_vehicle_id = event.get("vehicle_record_id")
            if event_vehicle_id and event_vehicle_id not in vehicle_ids:
                warnings.append(f"{component_id}: workshop event references vehicle record not present in this pilot: {event_vehicle_id}")

    if warnings:
        print("Warnings:")
        print("\n".join(f"- {warning}" for warning in warnings))
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {len(component_ids)} components and {len(vehicle_ids)} vehicles")


if __name__ == "__main__":
    main()
