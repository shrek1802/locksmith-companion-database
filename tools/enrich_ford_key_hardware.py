#!/usr/bin/env python3
"""Conservatively enrich Ford key hardware fields from existing IDs/text.

This pass only fills values that can be derived from data already present in each
record. It does not invent OEM part numbers or vehicle-specific key facts.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"

TRANSPONDERS = {
    "texas_4c": "Texas 4C",
    "texas_4d60": "Texas 4D-60",
    "texas_4d63_40bit": "Texas 4D-63 40-Bit",
    "texas_4d63_80bit": "Texas 4D-63 80-Bit DST80 (ID63 / 6F)",
    "nxp_hitag2_id46": "NXP Hitag2 ID46",
    "nxp_hitag_pro": "NXP Original PCF7939FA 128-Bit HITAG Pro (ID47 / may read ID49)",
    "hitag_aes": "NXP HITAG AES 128-Bit",
}

FREQUENCIES = {
    "mhz_433": "433 MHz",
    "mhz_433_92": "433.92 MHz",
    "mhz_434": "434 MHz",
    "mhz_315": "315 MHz",
}

BLADES = {
    "fo21": "FO21",
    "hu101": "HU101",
    "hu66": "HU66",
    "tibbe": "Tibbe",
}

BATTERY_RE = re.compile(r"\bCR(?:20(?:16|25|32)|24(?:30|50))\b", re.I)
BUTTON_RE = re.compile(r"\b([1-5])[- ]?button\b", re.I)


def has_value(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() not in {"unknown", "not verified", "verification required", "n/a"}
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def flatten_text(record: dict) -> str:
    bits = []
    info = record.get("vehicle_information", {})
    vehicle = record.get("vehicle", {})
    for value in (
        info.get("key_type"), info.get("notes"), info.get("battery_type"),
        info.get("frequency_mhz"), vehicle.get("variant"), vehicle.get("generation"),
    ):
        if isinstance(value, str):
            bits.append(value)
    for value in info.get("aftermarket_references", []) or []:
        if isinstance(value, str):
            bits.append(value)
    return " | ".join(bits)


def main() -> int:
    stats = {"records_changed": 0, "transponder_type": 0, "frequency_mhz": 0, "blade_profile": 0, "battery_type": 0, "button_count": 0}

    for path in sorted(FORD_ROOT.glob("*/models.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        changed_file = False
        for record in data.get("items", {}).values():
            if not isinstance(record, dict):
                continue
            info = record.setdefault("vehicle_information", {})
            changed = False

            if not has_value(info.get("transponder_type")):
                value = TRANSPONDERS.get(str(info.get("transponder_id") or ""))
                if value:
                    info["transponder_type"] = value
                    info.setdefault("immobiliser_generation", value)
                    stats["transponder_type"] += 1
                    changed = True

            if not has_value(info.get("frequency_mhz")):
                value = FREQUENCIES.get(str(info.get("frequency_id") or ""))
                if value:
                    info["frequency_mhz"] = value
                    stats["frequency_mhz"] += 1
                    changed = True

            if not has_value(info.get("blade_profile")):
                value = BLADES.get(str(info.get("blade_id") or ""))
                if value:
                    info["blade_profile"] = value
                    stats["blade_profile"] += 1
                    changed = True

            text = flatten_text(record)
            if not has_value(info.get("battery_type")):
                match = BATTERY_RE.search(text)
                if match:
                    info["battery_type"] = match.group(0).upper()
                    stats["battery_type"] += 1
                    changed = True

            if not has_value(info.get("button_count")):
                match = BUTTON_RE.search(text)
                if match:
                    info["button_count"] = int(match.group(1))
                    stats["button_count"] += 1
                    changed = True

            if changed:
                record.setdefault("verification", {})["hardware_enrichment"] = "derived_from_existing_record_data"
                stats["records_changed"] += 1
                changed_file = True

        if changed_file:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
