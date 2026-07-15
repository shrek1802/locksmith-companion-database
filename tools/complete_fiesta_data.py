#!/usr/bin/env python3
"""Clean and complete the UK Ford Fiesta locksmith records used by the app."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT / "database/vehicles/ford/fiesta/models.json"
PROCEDURES = ROOT / "database/vehicles/ford/fiesta/procedures.json"
MODEL_MANIFEST = ROOT / "database/vehicles/ford/fiesta/manifest.json"
FORD_MANIFEST = ROOT / "database/vehicles/ford/manifest.json"
ROOT_MANIFEST = ROOT / "manifest.json"
TODAY = "2026-07-15"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def set_info(item, **values):
    info = item.setdefault("vehicle_information", {})
    for key, value in values.items():
        info[key] = value
    item.setdefault("verification", {})["last_verified"] = TODAY


def main() -> None:
    data = load(MODELS)
    items = data["items"]

    # Remove duplicate workbook-generated records. The canonical year/ignition
    # records below contain the richer, split and app-ready data.
    duplicate_keys = {
        "fiesta_1998_2002_keyed",
        "fiesta_mk6_2002_2008_keyed",
        "fiesta_mk7_2008_2017_keyed",
        "fiesta_mk7_keyless_2008_2017_passive",
        "fiesta_mk8_2017_2023_keyed",
        "fiesta_mk8_2017_2023_passive",
    }
    for key in duplicate_keys:
        items.pop(key, None)

    common_legacy_tools = [
        "autel_im508s",
        "xhorse_key_tool_plus",
        "obdstar_g3",
        "xtool_x100_pad2",
    ]
    common_modern_tools = [
        "autel_im508s",
        "xhorse_key_tool_plus",
        "obdstar_g3",
        "xtool_x100_pad2",
        "lonsdor_k518",
    ]

    # Mk4/Mk5: keep a guarded legacy record but make the job route useful.
    legacy = items["fiesta_1995_2001_keyed"]
    set_info(
        legacy,
        immobiliser_system="Ford PATS legacy (Texas 4C family on later builds)",
        immobiliser_generation="Early PATS; confirm exact build before generating chip",
        transponder_type="Texas 4C on commonly encountered later Mk4/Mk5 builds — verify vehicle",
        transponder_id="texas_4c",
        frequency_mhz="433.92 where factory remote fitted",
        frequency_id="mhz_433_92",
        blade_profile="FO21",
        blade_id="fo21",
        oem_part_numbers=["1337641", "1753886"],
        tool_ids=common_legacy_tools,
        tool_or_cable_required="Standard OBD connection; stable battery support recommended",
        programming={
            "add_key":"OBD PATS programming on supported builds; cloning may also be possible",
            "all_keys_lost":"OBD/legacy PATS security-access route; confirm exact model year",
            "route":"OBD diagnostic or legacy PATS procedure",
            "online_requirement":"No",
        },
        notes="Confirm the exact build and chip before cutting or generating because this range crosses early PATS changes.",
    )

    # Mk6 UK: one clean record, FO21 and Texas 4D-63 40-bit.
    mk6 = items["fiesta_2002_2008_keyed"]
    set_info(
        mk6,
        immobiliser_system="Ford PATS Texas Crypto 4D",
        immobiliser_generation="Texas 4D-63 40-bit",
        transponder_type="Texas 4D-63 40-Bit (ID63)",
        transponder_id="texas_4d63_40bit",
        frequency_mhz="433.92",
        blade_profile="FO21",
        blade_id="fo21",
        key_type="3-button remote head key",
        button_count=3,
        battery_type="CR2032 — confirm physical remote",
        oem_part_numbers=["164-R8042", "5913139"],
        tool_ids=common_legacy_tools,
        tool_or_cable_required="Standard OBD connection; battery support recommended",
        programming={
            "add_key":"OBD PATS programming with a compatible Ford immobiliser tool",
            "all_keys_lost":"OBD PATS AKL supported; timed/security access may be required",
            "route":"OBD diagnostic immobiliser programming; remote matching may be manual/tool dependent",
            "online_requirement":"No",
        },
        notes="Use FO21 and Texas 4D-63 40-bit for this UK Mk6 record. Do not also show the conflicting HU101 duplicate.",
    )

    # Mk7 early and facelift keyed/passive records.
    for key in ("fiesta_2008_2012_keyed", "fiesta_2008_2012_passive"):
        item = items[key]
        info = item["vehicle_information"]
        info["tool_ids"] = common_legacy_tools
        info["tool_or_cable_required"] = "Standard OBD connection; battery support recommended"
        info["programming"] = {
            "add_key":"OBD PATS programming with a compatible Ford immobiliser tool",
            "all_keys_lost":"OBD PATS AKL supported; timed security access may apply",
            "route":"OBD diagnostic immobiliser programming",
            "online_requirement":"No",
        }
        item["verification"]["last_verified"] = TODAY

    for key in ("fiesta_2013_2017_keyed", "fiesta_2013_2017_passive"):
        item = items[key]
        info = item["vehicle_information"]
        info["transponder_type"] = "Texas 4D-63 80-Bit DST80 (ID63 / 6F)"
        info["tool_ids"] = common_legacy_tools
        info["tool_or_cable_required"] = "Standard OBD connection; battery support recommended"
        info["programming"] = {
            "add_key":"OBD PATS programming with a compatible Ford immobiliser tool",
            "all_keys_lost":"OBD PATS AKL supported; security access may apply",
            "route":"OBD diagnostic immobiliser programming",
            "online_requirement":"Normally no",
        }
        item["verification"]["last_verified"] = TODAY

    # Mk8: use the full chip name requested for stock identification. Keep tool
    # coverage guarded by exact build because Ford security access varies.
    for key in ("fiesta_2017_2023_keyed", "fiesta_2017_2023_passive"):
        item = items[key]
        info = item["vehicle_information"]
        info["immobiliser_system"] = "Ford PATS Hitag Pro"
        info["immobiliser_generation"] = "NXP 128-bit Hitag Pro / ID47-ID49 family"
        info["transponder_type"] = "NXP Original PCF7939FA 128-Bit HITAG Pro (ID47 / may read ID49)"
        info["transponder_id"] = "nxp_hitag_pro_pcf7939fa"
        info["tool_ids"] = common_modern_tools
        info["tool_or_cable_required"] = "Standard OBD connection; stable battery support. Confirm exact tool software and any Ford security access requirement."
        info["programming"] = {
            "add_key":"OBD programming where the selected tool explicitly supports the exact Fiesta build",
            "all_keys_lost":"OBD AKL where exact-build coverage is confirmed; later builds may require Ford online/security access",
            "route":"OBD diagnostic programming — select exact year, ignition type and build",
            "online_requirement":"Build and operation dependent",
        }
        info["chip_stock_note"] = "Standalone/common chip reference: NXP PCF7939FA. Integrated remote boards can use related NXP Hitag Pro variants; confirm the physical key/part number."
        item["verification"]["last_verified"] = TODAY

    data["updated_at"] = TODAY
    save(MODELS, data)

    # Replace the sparse procedure file with useful, non-destructive job cards.
    procedures = load(PROCEDURES)
    procedures["updated_at"] = TODAY
    procedures["items"] = {}
    for record_key, record in items.items():
        info = record["vehicle_information"]
        programming = info.get("programming", {})
        procedures["items"][record_key] = {
            "record_id": record["record_id"],
            "add_key": {
                "display_name":"Add Key",
                "overall_status":"supported_with_conditions",
                "method": programming.get("add_key"),
                "programming_route": programming.get("route"),
                "online_requirement": programming.get("online_requirement"),
                "obd_required": True,
                "battery_support_required": True,
                "supported_tools": info.get("tool_ids", []),
                "warnings":["Confirm exact year, ignition type, key frequency and transponder before programming."],
            },
            "all_keys_lost": {
                "display_name":"All Keys Lost",
                "overall_status":"supported_with_conditions",
                "method": programming.get("all_keys_lost"),
                "programming_route": programming.get("route"),
                "online_requirement": programming.get("online_requirement"),
                "obd_required": True,
                "battery_support_required": True,
                "supported_tools": info.get("tool_ids", []),
                "warnings":["Maintain stable vehicle voltage and confirm tool coverage before erasing or learning keys."],
            },
        }
    save(PROCEDURES, procedures)

    model_manifest = load(MODEL_MANIFEST)
    model_manifest["version"] = int(model_manifest.get("version", 0)) + 1
    model_manifest["updated_at"] = TODAY
    model_manifest["status"] = "job_fields_completed"
    model_manifest.setdefault("verification", {})["scope"] = "Duplicate Fiesta records removed; job, tool and transponder fields completed for app testing"
    model_manifest["verification"]["last_verified"] = TODAY
    save(MODEL_MANIFEST, model_manifest)

    ford = load(FORD_MANIFEST)
    ford["version"] = int(ford.get("version", 0)) + 1
    ford["updated_at"] = TODAY
    if "fiesta" in ford.get("models", {}):
        ford["models"]["fiesta"]["version"] = model_manifest["version"]
        ford["models"]["fiesta"]["status"] = "job_fields_completed"
    save(FORD_MANIFEST, ford)

    root = load(ROOT_MANIFEST)
    root["updated_at"] = TODAY
    root["manufacturers"]["ford"]["version"] = ford["version"]
    root["manufacturers"]["ford"]["status"] = "fiesta_job_fields_completed"
    save(ROOT_MANIFEST, root)

    print(f"Fiesta complete: {len(items)} canonical records; duplicates removed: {len(duplicate_keys)}")


if __name__ == "__main__":
    main()
