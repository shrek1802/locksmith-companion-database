#!/usr/bin/env python3
"""Populate app-visible Ford tool data and normalise exact programmer IDs."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORD = ROOT / "database" / "vehicles" / "ford"
ROOT_MANIFEST = ROOT / "manifest.json"
FORD_MANIFEST = FORD / "manifest.json"

TOOL_NAMES = {
    "autel_im508s": "Autel IM508S + XP400 Pro",
    "autel_im508s_xp400_pro": "Autel IM508S + XP400 Pro",
    "autel_km100x": "Autel KM100X",
    "xhorse_key_tool_max_pro": "Xhorse Key Tool Max Pro",
    "xhorse_key_tool_plus": "Xhorse Key Tool Plus",
    "keydiy_kd_x4": "KEYDIY KD-X4",
    "xtool_x100_pad2": "Xtool X100 Pad 2",
    "xtool_x100_pads": "Xtool X100 PAD S",
    "obdstar_g3": "OBDSTAR G3",
    "lonsdor_k518": "Lonsdor K518",
}

# Tools that can generate/prepare remotes or transponders even where they are not
# the primary vehicle-programming device.
GENERATION_TOOLS = [
    "autel_km100x",
    "xhorse_key_tool_max_pro",
    "keydiy_kd_x4",
]


def unique(values):
    out = []
    for value in values:
        if value and value not in out:
            out.append(value)
    return out


def update_models(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    for record in data.get("items", {}).values():
        info = record.setdefault("vehicle_information", {})
        existing_ids = list(info.get("tool_ids") or [])

        # Normalise generic/older IDs to the exact tools represented in Settings.
        replacements = {
            "autel_im508s": "autel_im508s_xp400_pro",
            "xtool_x100_pad2": "xtool_x100_pads",
            "xtool": "xtool_x100_pads",
            "obdstar": "obdstar_g3",
            "lonsdor": "lonsdor_k518",
        }
        normalised = [replacements.get(tool_id, tool_id) for tool_id in existing_ids]

        # Keep diagnostic programmers already verified for the record, while also
        # exposing the user's key-generation tools as generation/preparation tools.
        all_ids = unique(normalised + GENERATION_TOOLS)
        if all_ids != existing_ids:
            info["tool_ids"] = all_ids
            changed = True

        programming = info.get("programming") or {}
        connection = info.get("tool_or_cable_required") or "Confirm exact connection/cable for the selected vehicle and operation"

        supported = []
        owned_capable = []
        generation = []
        for tool_id in all_ids:
            item = {
                "id": tool_id,
                "name": TOOL_NAMES.get(tool_id, tool_id.replace("_", " ").title()),
            }
            if tool_id in GENERATION_TOOLS:
                item["capability"] = "Key/remote generation or preparation; vehicle programming coverage is operation dependent"
                generation.append(item)
            else:
                item["capability"] = "Vehicle key programming support recorded for this application; confirm exact tool menu/build"
                supported.append(item)
            if tool_id in {
                "autel_im508s_xp400_pro",
                "autel_km100x",
                "xhorse_key_tool_max_pro",
                "keydiy_kd_x4",
                "xtool_x100_pads",
            }:
                owned_capable.append(tool_id)

        tools = {
            "supported_programmers": supported,
            "key_generation_tools": generation,
            "owned_tool_match_ids": unique(owned_capable),
            "connection_or_adapter": connection,
            "battery_support": "Recommended during immobiliser programming",
            "programming_route": programming.get("route", "Confirm exact route"),
            "online_requirement": programming.get("online_requirement", "Confirm exact build/operation"),
            "note": "The app should compare these IDs with the tools selected in Settings and prioritise owned matches.",
        }
        if record.get("tools") != tools:
            record["tools"] = tools
            changed = True

    if changed:
        data["updated_at"] = "2026-07-15"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed


def bump(path: Path, status: str) -> None:
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    data["version"] = int(data.get("version", 0)) + 1
    data["updated_at"] = "2026-07-15"
    data["status"] = status
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    changed_models = []
    for path in sorted(FORD.glob("*/models.json")):
        if update_models(path):
            changed_models.append(path.parent.name)
            manifest = path.parent / "manifest.json"
            if manifest.exists():
                bump(manifest, "tool_display_populated")

    if changed_models:
        bump(FORD_MANIFEST, "tool_display_populated")
        root = json.loads(ROOT_MANIFEST.read_text(encoding="utf-8"))
        ford_entry = root.setdefault("manufacturers", {}).setdefault("ford", {})
        ford_entry["version"] = int(ford_entry.get("version", 0)) + 1
        ford_entry["status"] = "tool_display_populated"
        root["updated_at"] = "2026-07-15"
        ROOT_MANIFEST.write_text(json.dumps(root, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"changed_models": changed_models, "count": len(changed_models)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
