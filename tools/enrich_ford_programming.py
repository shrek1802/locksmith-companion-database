#!/usr/bin/env python3
"""Fill missing Ford programming fields with conservative UK-market baselines.

This does not overwrite richer record-specific data. Added values are explicitly marked
as baseline guidance so the app is useful without presenting unverified tool-menu detail
as personally confirmed fact.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"
TODAY = date.today().isoformat()


def has_value(value) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() not in {
            "unknown", "not verified", "verification required", "awaiting verification"
        }
    return bool(value) if isinstance(value, (list, dict)) else True


def year_for(record: dict) -> int:
    vehicle = record.get("vehicle", {})
    for key in ("year_to", "year_from"):
        value = vehicle.get(key)
        if isinstance(value, int):
            return value
    return 2015


def is_smart(record: dict) -> bool:
    info = record.get("vehicle_information", {})
    text = " ".join(
        str(value or "") for value in (
            info.get("key_type"),
            record.get("vehicle", {}).get("variant"),
            record.get("vehicle", {}).get("generation"),
        )
    ).lower()
    return bool(info.get("smart_key")) or any(word in text for word in ("smart", "proximity", "keyless", "push button"))


def baseline(record: dict) -> dict[str, str]:
    year = year_for(record)
    smart = is_smart(record)
    module = "KVM/BCM" if smart else "BCM/IPC PATS"

    if year <= 2001:
        return {
            "add_key": "Use the supported Ford PATS OBD menu where available; transponder cloning is an alternative on compatible legacy chips.",
            "all_keys_lost": "Use the legacy Ford PATS security-access route. Some early systems may require chip/module work when OBD coverage is unavailable.",
            "route": "Legacy Ford PATS by OBD, with clone or module/chip fallback where required.",
            "online_requirement": "No online account normally required.",
        }
    if year <= 2018:
        return {
            "add_key": f"Program through the {module} using a supported Ford immobiliser OBD menu. Keep an existing key available when adding.",
            "all_keys_lost": f"AKL is normally completed through the {module} by OBD. Timed security access or an erase-and-program sequence may apply.",
            "route": f"Standard OBD Ford PATS programming through the {module}; use regulated battery support.",
            "online_requirement": "Normally no for supported aftermarket-tool programming.",
        }
    if year <= 2022:
        return {
            "add_key": f"Use the supported Ford {module} OBD immobiliser menu. Platform security access and an internet connection may be tool-dependent.",
            "all_keys_lost": f"Use the supported {module} AKL route by OBD where covered. Later platforms may need online calculation, server access or a platform-specific cable.",
            "route": f"OBD programming through the {module}; confirm platform, CAN/CAN-FD connection and current tool coverage before starting.",
            "online_requirement": "Tool/platform dependent; some routes are offline, while later Ford security functions may require internet or FDRS.",
        }
    return {
        "add_key": f"Use current supported coverage for the {module}. Online security authorisation/FDRS may be required on this generation.",
        "all_keys_lost": f"AKL requires current confirmed coverage for the {module}; online Ford security access, FDRS or dealer-level authorisation may apply.",
        "route": f"Late Ford secured OBD route through the {module}; confirm CAN-FD, gateway and online requirements before accepting the job.",
        "online_requirement": "Online/FDRS commonly applies; confirm the exact vehicle and current tool subscription before work.",
    }


def enrich_record(record: dict) -> bool:
    info = record.setdefault("vehicle_information", {})
    programming = info.setdefault("programming", {})
    values = baseline(record)
    changed = False
    added = []

    for field in ("add_key", "all_keys_lost", "route", "online_requirement"):
        if not has_value(programming.get(field)):
            programming[field] = values[field]
            added.append(field)
            changed = True

    if added:
        programming["data_status"] = "uk_baseline_guidance_not_personally_verified"
        programming["last_baseline_update"] = TODAY
        programming["verification_note"] = (
            "Confirm exact year, ignition type, module generation and current tool menu before programming. "
            "Record-specific verified information takes priority over this baseline."
        )
        notes = record.setdefault("notes", {})
        notes["programming_baseline"] = (
            "Programming fields marked as UK baseline guidance must be checked against the exact vehicle and current tool coverage."
        )
        changed = True

    return changed


def main() -> int:
    changed_records = 0
    changed_files = 0
    fields_added = {"add_key": 0, "all_keys_lost": 0, "route": 0, "online_requirement": 0}

    for path in sorted(FORD_ROOT.glob("*/models.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        file_changed = False
        for record in data.get("items", {}).values():
            if not isinstance(record, dict):
                continue
            before = dict(record.get("vehicle_information", {}).get("programming", {}) or {})
            if enrich_record(record):
                after = record["vehicle_information"]["programming"]
                for field in fields_added:
                    if not has_value(before.get(field)) and has_value(after.get(field)):
                        fields_added[field] += 1
                changed_records += 1
                file_changed = True
        if file_changed:
            data["updated_at"] = TODAY
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            changed_files += 1

    print(json.dumps({
        "changed_files": changed_files,
        "changed_records": changed_records,
        "fields_added": fields_added,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
