#!/usr/bin/env python3
"""Promote Ford vehicle_information.tool_ids into app-visible top-level tools.

The Android app's Tools tile reads record.tools. Older/generated records stored
only vehicle_information.tool_ids, so the tile appeared empty even when the
compatibility IDs were present.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"
ROOT_MANIFEST = ROOT / "manifest.json"
FORD_MANIFEST = FORD_ROOT / "manifest.json"
TODAY = "2026-07-15"

TOOL_LABELS = {
    "autel_im508s": "Autel IM508S + XP400 Pro",
    "xhorse_key_tool_plus": "Xhorse Key Tool Plus",
    "xhorse_key_tool_max_plus": "Xhorse Key Tool Max Plus",
    "keydiy_kd_x4": "KEYDIY KD-X4",
    "obdstar_g3": "OBDSTAR G3",
    "xtool_x100_pad2": "Xtool X100 Pad 2",
    "lonsdor_k518": "Lonsdor K518",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_tools(info: dict[str, Any]) -> dict[str, Any]:
    tool_ids = info.get("tool_ids") or []
    tools: dict[str, Any] = {}
    for tool_id in tool_ids:
        label = TOOL_LABELS.get(str(tool_id), str(tool_id).replace("_", " ").title())
        tools[label] = "Compatible family coverage — confirm exact year, ignition type and current tool menu"

    cable = info.get("tool_or_cable_required")
    if cable:
        tools["Connection / cable"] = cable

    programming = info.get("programming") or {}
    route = programming.get("route")
    if route:
        tools["Programming route"] = route

    online = programming.get("online_requirement")
    if online not in (None, ""):
        tools["Online / FDRS"] = online

    if tools:
        tools["Battery support"] = "Use a regulated vehicle support supply during immobiliser programming"
    return tools


def bump_manifest(path: Path, status: str) -> None:
    if not path.exists():
        return
    data = load(path)
    data["version"] = int(data.get("version", 0)) + 1
    data["updated_at"] = TODAY
    data["status"] = status
    save(path, data)


def main() -> int:
    changed_models: list[str] = []
    changed_records = 0

    for models_path in sorted(FORD_ROOT.glob("*/models.json")):
        data = load(models_path)
        model_changed = False
        for record in (data.get("items") or {}).values():
            info = record.get("vehicle_information") or {}
            promoted = build_tools(info)
            if promoted and record.get("tools") != promoted:
                record["tools"] = promoted
                model_changed = True
                changed_records += 1

        if not model_changed:
            continue

        data["updated_at"] = TODAY
        save(models_path, data)
        model_dir = models_path.parent
        bump_manifest(model_dir / "manifest.json", "tool_data_promoted")
        changed_models.append(model_dir.name)

    if changed_models:
        bump_manifest(FORD_MANIFEST, "tool_data_promoted")
        if ROOT_MANIFEST.exists():
            root = load(ROOT_MANIFEST)
            ford = (root.setdefault("manufacturers", {})).setdefault("ford", {})
            ford["version"] = int(ford.get("version", 0)) + 1
            ford["status"] = "tool_data_promoted"
            root["updated_at"] = TODAY
            save(ROOT_MANIFEST, root)

    report = {
        "updated_at": TODAY,
        "changed_models": changed_models,
        "changed_record_count": changed_records,
    }
    save(FORD_ROOT / "FORD_TOOL_PROMOTION_REPORT.json", report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
