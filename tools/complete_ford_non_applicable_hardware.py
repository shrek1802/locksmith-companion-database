#!/usr/bin/env python3
"""Resolve Ford hardware fields that are genuinely non-applicable or variable.

This pass does not invent part numbers or vehicle-specific remote specifications. It
only replaces empty button/battery fields where the record itself clearly describes
one of these cases:
- a mechanical/transponder key with a separate remote;
- a key without an integrated remote;
- a configuration whose remote varies by build.

The resulting wording is useful in the app and prevents a non-applicable field from
being presented as missing data.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"
TODAY = date.today().isoformat()

INVALID = {"", "unknown", "not verified", "verification required", "n/a"}


def missing(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in INVALID
    return False


def combined_text(record: dict) -> str:
    info = record.get("vehicle_information", {})
    vehicle = record.get("vehicle", {})
    values = [
        info.get("key_type"),
        info.get("notes"),
        info.get("transponder_type"),
        vehicle.get("variant"),
        vehicle.get("generation"),
    ]
    return " ".join(str(v or "") for v in values).lower()


def classify(text: str) -> str | None:
    separate_markers = (
        "separate remote",
        "separate or integrated remote",
        "remote depending build",
        "remote varies",
        "factory remote fitted",
    )
    mechanical_only_markers = (
        "mechanical transponder key",
        "plain transponder key",
        "non-remote key",
        "mechanical ignition key only",
        "service key",
    )
    if any(marker in text for marker in separate_markers):
        return "variable"
    if any(marker in text for marker in mechanical_only_markers):
        return "not_integrated"
    return None


def main() -> int:
    changed_records = 0
    updates = {"button_count": 0, "battery_type": 0}

    for path in sorted(FORD_ROOT.glob("*/models.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        dirty = False
        for record in data.get("items", {}).values():
            if not isinstance(record, dict):
                continue
            info = record.setdefault("vehicle_information", {})
            kind = classify(combined_text(record))
            if not kind:
                continue

            record_changed = False
            if missing(info.get("button_count")):
                if kind == "variable":
                    info["button_count"] = "Varies by separate/original remote configuration"
                else:
                    info["button_count"] = "Not applicable to the mechanical transponder key"
                updates["button_count"] += 1
                record_changed = True

            if missing(info.get("battery_type")):
                if kind == "variable":
                    info["battery_type"] = "Match the separate/original remote; not defined by the transponder key"
                else:
                    info["battery_type"] = "No battery in the mechanical transponder key"
                updates["battery_type"] += 1
                record_changed = True

            if record_changed:
                verification = record.setdefault("verification", {})
                verification["non_applicable_hardware_resolved_at"] = TODAY
                verification["non_applicable_hardware_basis"] = "existing key/remote description"
                changed_records += 1
                dirty = True

        if dirty:
            data["updated_at"] = TODAY
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    report = {
        "completed_at": TODAY,
        "changed_records": changed_records,
        "updates": updates,
        "policy": "Only non-applicable or explicitly variable hardware was resolved; no OEM numbers were invented.",
    }
    out = ROOT / "reports" / "ford_non_applicable_hardware_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
