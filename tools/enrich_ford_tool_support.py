#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"
TODAY = date.today().isoformat()

PRIMARY_BY_ERA = {
    "legacy": [
        "autel_im508s_xp400_pro",
        "xtool_x100_pad2",
        "obdstar_g3",
        "smart_pro",
    ],
    "mid": [
        "autel_im508s_xp400_pro",
        "xhorse_key_tool_plus",
        "xtool_x100_pad2",
        "obdstar_g3",
        "lonsdor_k518_pro",
        "smart_pro",
    ],
    "late": [
        "autel_im508s_xp400_pro",
        "xhorse_key_tool_plus",
        "obdstar_g3",
        "smart_pro",
    ],
}

GENERATION_TOOLS = [
    "autel_km100x",
    "xhorse_key_tool_max_pro",
    "keydiy_kd_x4",
]

TOOL_NAMES = {
    "autel_im508s_xp400_pro": "Autel IM508S + XP400 Pro",
    "autel_km100x": "Autel KM100 / KM100X",
    "xhorse_key_tool_max_pro": "Xhorse Key Tool Max Pro",
    "xhorse_key_tool_plus": "Xhorse Key Tool Plus",
    "keydiy_kd_x4": "KEYDIY KD-X4",
    "xtool_x100_pad2": "Xtool X100 Pad 2",
    "obdstar_g3": "OBDSTAR G3",
    "lonsdor_k518_pro": "Lonsdor K518 Pro",
    "smart_pro": "Advanced Diagnostics Smart Pro",
}


def era_for(record: dict) -> str:
    year_to = record.get("vehicle", {}).get("year_to")
    year_from = record.get("vehicle", {}).get("year_from")
    year = year_to if isinstance(year_to, int) else year_from if isinstance(year_from, int) else 2015
    if year <= 2010:
        return "legacy"
    if year <= 2020:
        return "mid"
    return "late"


def unique(values):
    out = []
    seen = set()
    for value in values:
        if value and value not in seen:
            out.append(value)
            seen.add(value)
    return out


def enrich_record(record: dict) -> bool:
    info = record.setdefault("vehicle_information", {})
    changed = False

    current = info.get("tool_ids") if isinstance(info.get("tool_ids"), list) else []
    if not current:
        info["tool_ids"] = PRIMARY_BY_ERA[era_for(record)]
        current = info["tool_ids"]
        changed = True

    if info.get("key_type") or info.get("transponder_type"):
        if info.get("generation_tool_ids") != GENERATION_TOOLS:
            info["generation_tool_ids"] = GENERATION_TOOLS
            changed = True

    tools = record.setdefault("tools", {})
    supported = []
    for tool_id in unique(current):
        supported.append({
            "id": tool_id,
            "name": TOOL_NAMES.get(tool_id, tool_id.replace("_", " ").title()),
            "role": "immobiliser_programming",
            "status": "coverage_candidate_confirm_exact_menu",
        })
    for tool_id in GENERATION_TOOLS:
        supported.append({
            "id": tool_id,
            "name": TOOL_NAMES[tool_id],
            "role": "remote_or_transponder_generation",
            "status": "generation_only_not_akl_claim",
        })

    if tools.get("supported_tools") != supported:
        tools["supported_tools"] = supported
        changed = True
    all_ids = unique(current + GENERATION_TOOLS)
    if tools.get("tool_ids") != all_ids:
        tools["tool_ids"] = all_ids
        changed = True
    tools["Important"] = "Programming coverage varies by exact year, ignition type and current tool software. Generation tools do not automatically mean Add Key or AKL support."

    return changed


def main() -> int:
    changed_records = 0
    changed_files = 0
    for path in sorted(FORD_ROOT.glob("*/models.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        file_changed = False
        for record in data.get("items", {}).values():
            if isinstance(record, dict) and enrich_record(record):
                changed_records += 1
                file_changed = True
        if file_changed:
            data["updated_at"] = TODAY
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            changed_files += 1

    print(json.dumps({"changed_files": changed_files, "changed_records": changed_records}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
