#!/usr/bin/env python3
"""Validate standalone Database V3 workshop evidence files."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "workshop_events"
COMPONENTS = ROOT / "components"
VALID_RESULTS = {"success", "partial", "failed", "not_attempted"}
VALID_SCOPES = {"exact_vehicle", "related_platform"}


def load(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def valid_date(value) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def main() -> None:
    component_ids = {
        load(path).get("id")
        for path in COMPONENTS.rglob("*.json")
    }
    errors = []
    warnings = []
    event_ids = set()
    event_count = 0

    for path in sorted(EVENTS.glob("*.json")):
        if path.name.endswith(".template.json"):
            continue
        event_count += 1
        event = load(path)
        event_id = event.get("event_id")
        if not event_id:
            errors.append(f"{path}: event_id is required")
        elif event_id in event_ids:
            errors.append(f"{path}: duplicate event_id {event_id}")
        event_ids.add(event_id)

        if event.get("result") not in VALID_RESULTS:
            errors.append(f"{event_id}: invalid result {event.get('result')}")
        if event.get("evidence_scope") not in VALID_SCOPES:
            errors.append(f"{event_id}: evidence_scope must be exact_vehicle or related_platform")

        vehicle = event.get("vehicle", {})
        if vehicle.get("market") != "UK" or vehicle.get("steering") != "RHD":
            errors.append(f"{event_id}: vehicle must be UK/RHD")
        for field in ("manufacturer", "model", "year"):
            if vehicle.get(field) in (None, ""):
                errors.append(f"{event_id}: vehicle.{field} is required")

        tool = event.get("tool", {})
        if not tool.get("manufacturer") or not tool.get("model"):
            errors.append(f"{event_id}: exact tool manufacturer and model are required")
        if not event.get("operation"):
            errors.append(f"{event_id}: operation is required")
        if not valid_date(event.get("completed_at")):
            errors.append(f"{event_id}: completed_at must be an ISO date")

        linked = event.get("component_ids")
        if not isinstance(linked, list) or not linked:
            errors.append(f"{event_id}: component_ids must contain at least one component")
        else:
            unknown = sorted(set(linked) - component_ids)
            if unknown:
                errors.append(f"{event_id}: unknown component_ids {unknown}")

        if event.get("evidence_scope") == "exact_vehicle" and not event.get("vehicle_record_id"):
            errors.append(f"{event_id}: exact_vehicle evidence requires vehicle_record_id")
        if event.get("result") == "not_attempted":
            warnings.append(f"{event_id}: not_attempted events do not verify a procedure")

    if warnings:
        print("Warnings:")
        print("\n".join(f"- {warning}" for warning in warnings))
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {event_count} standalone workshop events")


if __name__ == "__main__":
    main()
