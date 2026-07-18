#!/usr/bin/env python3
"""Apply official Autel APB300 MLB working-key Add Key coverage to Audi."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDI = ROOT / "database" / "vehicles" / "audi"
SOURCE = "https://www.autel.com/u/cms/www/202602/12012616q4ru.pdf"
TARGETS = {
    "a4": "A4/S4/RS4 2017-present",
    "a5": "A5/S5/RS5 2017-present",
    "a6": "A6/S6/RS6 2019-present",
    "a7": "A7/S7 2019-present; RS7 2021-present",
    "a8": "A8/S8 2018-present",
    "q7": "Q7 2016-present",
    "q8": "Q8 2017-present",
}


def main() -> int:
    for model_id, coverage in TARGETS.items():
        path = AUDI / model_id / "procedures.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        add_key = next(item for item in data["procedures"] if item["id"] == "add_key")
        support = [item for item in add_key.get("tool_support", []) if item.get("tool") != "Autel APB300 with MaxiIM 508/608 series"]
        support.append({
            "tool": "Autel APB300 with MaxiIM 508/608 series",
            "status": "partially_verified",
            "source": SOURCE,
            "confidence": "high",
            "coverage": coverage,
            "operation": "Add Key",
            "working_key_required": True,
            "method": "Read immobiliser data from the opened original working key; no instrument-cluster removal for this route.",
            "required_hardware": ["Autel APB300", "Compatible MaxiIM 508/608-series tablet", "Supported Autel IKEY or key PCB"],
            "limits": "Official coverage is model/year and Add Key specific. It does not verify AKL, every trim/key PCB, UK RHD locations or unrelated generations.",
            "checked_at": "2026-07-18",
        })
        add_key["tool_support"] = support
        add_key["status"] = "partially_verified"
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"updated {len(TARGETS)} Audi MLB Add Key records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
