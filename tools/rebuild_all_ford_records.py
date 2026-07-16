#!/usr/bin/env python3
"""Rebuild every Ford models.json into the app's complete Locksmith Card shape.

This script is deliberately conservative: it promotes existing verified data into the
sections the app consumes, normalises names/IDs, preserves richer existing fields,
and records any genuinely missing technical facts instead of inventing them.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"
TODAY = date.today().isoformat()

TOOL_NAMES = {
    "autel_im508": "Autel IM508",
    "autel_im508s": "Autel IM508S + XP400 Pro",
    "autel_im508s_xp400_pro": "Autel IM508S + XP400 Pro",
    "autel_im608": "Autel IM608",
    "autel_im608_pro": "Autel IM608 Pro",
    "autel_km100": "Autel KM100",
    "autel_km100x": "Autel KM100X",
    "xhorse_key_tool_max_pro": "Xhorse Key Tool Max Pro",
    "xhorse_key_tool_plus": "Xhorse Key Tool Plus",
    "xhorse_vvdi2": "Xhorse VVDI2",
    "xhorse_vvdi_prog": "Xhorse VVDI Prog",
    "keydiy_kd_x4": "KEYDIY KD-X4",
    "keydiy_kd_max": "KEYDIY KD-Max",
    "xtool_x100_pad2": "Xtool X100 Pad 2",
    "xtool_x100_max2": "Xtool X100 Max 2",
    "xtool_kc100": "Xtool KC100",
    "xtool_kc501": "Xtool KC501",
    "obdstar_g3": "OBDSTAR G3",
    "obdstar_x300_dp_plus": "OBDSTAR X300 DP Plus",
    "obdstar_key_master_dp_plus": "OBDSTAR Key Master DP Plus",
    "lonsdor_k518_pro": "Lonsdor K518 Pro",
    "lonsdor_kh100_plus": "Lonsdor KH100+",
    "tango": "Tango",
    "tmpro2": "TMPro2",
    "orange5": "Orange5",
    "smok_uhds": "SMOK UHDS",
    "yanhua_acdp1": "Yanhua ACDP 1",
    "yanhua_acdp2": "Yanhua ACDP 2",
    "avdi": "AVDI",
    "zed_full": "Zed-FULL",
    "smart_pro": "Advanced Diagnostics Smart Pro",
}

TRANSPONDER_NAMES = {
    "nxp_hitag_pro": "NXP Original PCF7939FA 128-Bit HITAG Pro (ID47 / may read ID49)",
    "texas_4d63_80bit": "Texas 4D-63 80-Bit DST80 (ID63 / 6F)",
    "texas_4d63_40bit": "Texas 4D-63 40-Bit",
    "texas_4d60": "Texas 4D-60",
    "texas_4c": "Texas 4C",
    "nxp_hitag2_id46": "NXP Hitag2 ID46",
    "hitag_aes": "NXP HITAG AES 128-Bit",
}

REQUIRED_VISIBLE_FIELDS = (
    "blade_profile",
    "transponder_type",
    "frequency_mhz",
    "key_type",
    "battery_type",
    "button_count",
    "oem_part_numbers",
)


def has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip()) and value.strip().lower() not in {
            "verification required", "not verified", "unknown", "n/a"
        }
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def normalise_transponder(info: dict[str, Any]) -> None:
    transponder_id = str(info.get("transponder_id") or "").strip()
    if transponder_id in TRANSPONDER_NAMES:
        info["transponder_type"] = TRANSPONDER_NAMES[transponder_id]
        info["immobiliser_generation"] = TRANSPONDER_NAMES[transponder_id]


def key_information(info: dict[str, Any]) -> dict[str, Any]:
    return {
        "key_type": info.get("key_type"),
        "blade_profile": info.get("blade_profile"),
        "transponder_type": info.get("transponder_type"),
        "transponder_id": info.get("transponder_id"),
        "frequency_mhz": info.get("frequency_mhz"),
        "battery": info.get("battery_type"),
        "buttons": info.get("button_count"),
        "emergency_blade": info.get("emergency_blade"),
        "smart_key": info.get("smart_key"),
        "oem_part_numbers": info.get("oem_part_numbers", []),
        "aftermarket_references": info.get("aftermarket_references", []),
    }


def operation_object(value: Any, route: Any, online: Any, cable: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        result = dict(value)
    else:
        result = {"method": value} if has_value(value) else {}
    if has_value(route):
        result.setdefault("programming_method", route)
    if has_value(online):
        result.setdefault("online_requirement", online)
    if has_value(cable):
        result.setdefault("connection_or_adapter", cable)
    return result


def operations(info: dict[str, Any], existing: dict[str, Any]) -> dict[str, Any]:
    programming = info.get("programming") if isinstance(info.get("programming"), dict) else {}
    route = programming.get("route")
    online = programming.get("online_requirement")
    cable = info.get("tool_or_cable_required")
    result = dict(existing) if isinstance(existing, dict) else {}
    result["add_key"] = operation_object(programming.get("add_key"), route, online, cable)
    result["all_keys_lost"] = operation_object(programming.get("all_keys_lost"), route, online, cable)
    if has_value(route):
        result["programming_route"] = route
    if has_value(online):
        result["online_requirement"] = online
    return result


def security(info: dict[str, Any], existing: dict[str, Any]) -> dict[str, Any]:
    programming = info.get("programming") if isinstance(info.get("programming"), dict) else {}
    result = dict(existing) if isinstance(existing, dict) else {}
    result.setdefault("family", info.get("immobiliser_system"))
    result.setdefault("generation", info.get("immobiliser_generation"))
    result.setdefault("transponder_family", info.get("transponder_type"))
    result.setdefault("programming_route", programming.get("route"))
    result.setdefault("online_requirement", programming.get("online_requirement"))
    online_text = str(programming.get("online_requirement") or "").lower()
    if "fdrs" in online_text or "online" in online_text:
        result.setdefault("fdrs_requirement", programming.get("online_requirement"))
    return {key: value for key, value in result.items() if has_value(value)}


def tools(info: dict[str, Any], existing: Any) -> dict[str, Any]:
    tool_ids = info.get("tool_ids") if isinstance(info.get("tool_ids"), list) else []
    existing_dict = dict(existing) if isinstance(existing, dict) else {}
    supported = []
    seen = set()

    for tool_id in tool_ids:
        tid = str(tool_id)
        name = TOOL_NAMES.get(tid, tid.replace("_", " ").title())
        if tid not in seen:
            supported.append({"id": tid, "name": name, "status": "listed_supported"})
            seen.add(tid)

    old_supported = existing_dict.get("supported_tools")
    if isinstance(old_supported, list):
        for item in old_supported:
            if isinstance(item, dict):
                tid = str(item.get("id") or item.get("tool_id") or item.get("name") or "")
                if tid and tid not in seen:
                    supported.append(item)
                    seen.add(tid)
            elif item:
                tid = str(item)
                if tid not in seen:
                    supported.append({"id": tid, "name": TOOL_NAMES.get(tid, tid), "status": "listed_supported"})
                    seen.add(tid)

    result = dict(existing_dict)
    result["supported_tools"] = supported
    result["tool_ids"] = [item.get("id") for item in supported if isinstance(item, dict) and item.get("id")]
    result["connection_or_adapter"] = info.get("tool_or_cable_required")
    programming = info.get("programming") if isinstance(info.get("programming"), dict) else {}
    result["programming_route"] = programming.get("route")
    result["online_requirement"] = programming.get("online_requirement")
    result["battery_support"] = "Recommended for immobiliser programming"
    return {key: value for key, value in result.items() if has_value(value)}


def notes(info: dict[str, Any], existing: Any, missing: list[str]) -> dict[str, Any]:
    result = dict(existing) if isinstance(existing, dict) else {}
    if has_value(info.get("notes")):
        result.setdefault("job_notes", info.get("notes"))
    if missing:
        result["data_gaps"] = missing
    return result


def rebuild_record(record: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    info = record.setdefault("vehicle_information", {})
    normalise_transponder(info)

    missing = [field for field in REQUIRED_VISIBLE_FIELDS if not has_value(info.get(field))]
    programming = info.get("programming") if isinstance(info.get("programming"), dict) else {}
    for field in ("add_key", "all_keys_lost", "route", "online_requirement"):
        if not has_value(programming.get(field)):
            missing.append(f"programming.{field}")
    if not info.get("tool_ids"):
        missing.append("tool_ids")

    record["key_information"] = key_information(info)
    record["operations"] = operations(info, record.get("operations", {}))
    record["security"] = security(info, record.get("security", {}))
    record["tools"] = tools(info, record.get("tools", {}))
    record["notes"] = notes(info, record.get("notes", {}), missing)
    record["record_completion"] = {
        "status": "complete_for_app" if not missing else "needs_targeted_verification",
        "missing_fields": missing,
        "rebuilt_at": TODAY,
        "pipeline": "rebuild_all_ford_records_v1",
    }
    verification = record.setdefault("verification", {})
    verification["last_checked"] = TODAY
    verification["app_schema_rebuilt"] = True
    return record, missing


def bump_manifest(path: Path) -> None:
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("version", "database_version"):
        if isinstance(data.get(key), int):
            data[key] += 1
    data["updated_at"] = TODAY
    data["status"] = "ford_full_record_rebuild"
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    report = {
        "rebuilt_at": TODAY,
        "model_files": 0,
        "records": 0,
        "records_complete_for_app": 0,
        "records_needing_targeted_verification": 0,
        "missing_field_counts": {},
        "models": {},
    }

    for models_path in sorted(FORD_ROOT.glob("*/models.json")):
        payload = json.loads(models_path.read_text(encoding="utf-8"))
        items = payload.get("items")
        if not isinstance(items, dict):
            continue
        model_missing = 0
        for record_id, record in items.items():
            if not isinstance(record, dict):
                continue
            rebuilt, missing = rebuild_record(record)
            items[record_id] = rebuilt
            report["records"] += 1
            if missing:
                report["records_needing_targeted_verification"] += 1
                model_missing += 1
            else:
                report["records_complete_for_app"] += 1
            for field in missing:
                report["missing_field_counts"][field] = report["missing_field_counts"].get(field, 0) + 1

        payload["updated_at"] = TODAY
        payload["rebuild_pipeline"] = "rebuild_all_ford_records_v1"
        models_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        report["model_files"] += 1
        report["models"][models_path.parent.name] = {
            "records": len(items),
            "records_needing_targeted_verification": model_missing,
        }
        bump_manifest(models_path.parent / "manifest.json")

    bump_manifest(FORD_ROOT / "manifest.json")
    bump_manifest(ROOT / "manifest.json")
    report_path = ROOT / "reports" / "ford_full_rebuild_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
