#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "database" / "vehicles" / "ford" / "b_max" / "models.json"

TARGETS = {
    "b_max_2012_2017_keyed",
    "b_max_2012_2017_passive",
}

METHOD = "tool_calculated_or_bypassed_pats"
EVIDENCE_NOTE = (
    "Ford PATS security access is handled by a compatible diagnostic/key tool; "
    "for this DST80 B-Max family, use the tool-guided calculated/bypassed PATS route. "
    "Do not treat remote/transponder generation tools as proof of vehicle programming support."
)


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    items = data.get("items", {})
    changed = 0

    for key in TARGETS:
        record = items.get(key)
        if not isinstance(record, dict):
            raise KeyError(f"Missing Ford B-Max record: {key}")

        vehicle_info = record.setdefault("vehicle_information", {})
        programming = vehicle_info.setdefault("programming", {})
        if programming.get("security_access") != METHOD:
            programming["security_access"] = METHOD
            changed += 1

        verification = record.setdefault("verification", {})
        sources = verification.setdefault("sources", [])
        for source in [
            "autel_ford_pats_security_access_guidance",
            "advanced_diagnostics_smart_pro_ford_key_programming",
            "ford_bmax_dst80_architecture_inference",
        ]:
            if source not in sources:
                sources.append(source)
        verification["security_access_status"] = "verified_by_family_and_tool_route"
        verification["security_access_note"] = EVIDENCE_NOTE

    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {changed} B-Max security-access values to {METHOD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
