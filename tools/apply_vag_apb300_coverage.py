#!/usr/bin/env python3
"""Apply official Autel APB300 working-key Add Key coverage conservatively."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VW = ROOT / "database" / "vehicles" / "volkswagen"
SOURCE = "https://www.autel.com/u/cms/www/202602/12012616q4ru.pdf"

# model: (top-level record container, generation id -> exact published coverage)
TARGETS = {
    "arteon": ("items", {"arteon_2017_2020": "2017-2020", "arteon_2020_present": "2020-2021 only"}),
    "golf": ("items", {"golf_mk7_2013_2017": "2013-2017", "golf_mk75_2017_2020": "2017-2020", "golf_mk8_2020_present": "2020-2021 only"}),
    "passat": ("procedures", {"passat_b8_2014_2019": "2015-2019 only", "passat_b8_facelift_2019_2023": "2019-2021 only"}),
    "polo": ("items", {"polo_aw_2017_2021": "2018-2021 only"}),
    "tiguan": ("items", {"tiguan_ad1_2016_2024": "2018-2021 only"}),
    "touran": ("items", {"touran_5t_2015_present": "2016-2022 only"}),
    "t_cross": ("items", {"t_cross_c11": "2018-2021"}),
    "t_roc": ("items", {"t_roc_a11_2017_2021": "2018-2021 only"}),
    "crafter": ("items", {"crafter_sy_sz_2017_present": "2017-2021 only"}),
}


def tool_record(model: str, coverage: str) -> dict:
    return {
        "status": "supported",
        "method": "working_key_data",
        "display_name": "Autel APB300 + MaxiIM 508/608 series",
        "summary": f"Official Autel APB300 working-key Add Key coverage lists Volkswagen {model} {coverage}.",
        "source": SOURCE,
        "confidence": "high",
        "checked_at": "2026-07-18",
        "vehicle_connection": {"required": False, "display_text": "Open and read the original working key using APB300"},
        "tool_accessory_ids": ["Autel APB300", "Compatible MaxiIM 508/608-series tablet", "Supported Autel VW/Audi-style IKEY or key PCB"],
        "working_key_required": True,
        "vehicle_required": False,
        "warnings": [
            "Coverage is Add Key only and does not establish All Keys Lost support.",
            "Confirm the exact key PCB and keyed or KESSY configuration before programming.",
            "Autel states no additional adapter is needed for the APB300 working-key data route.",
        ],
    }


def main() -> int:
    changed = 0
    for model, (container_name, records) in TARGETS.items():
        path = VW / model / "procedures.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        container = data[container_name]
        for generation_id, coverage in records.items():
            add_key = container[generation_id]["add_key"]
            add_key.setdefault("tools", {})["autel_apb300"] = tool_record(data.get("model", model), coverage)
            changed += 1
        data["updated_at"] = "2026-07-18"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"updated {changed} Volkswagen Add Key records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
