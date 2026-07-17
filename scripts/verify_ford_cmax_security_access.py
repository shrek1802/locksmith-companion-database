#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "database" / "vehicles" / "ford" / "c_max" / "models.json"

TARGET_IDS = {
    "ford_c_max_2003_2010_keyed_uk",
    "ford_c_max_2010_2014_keyed_uk",
    "ford_c_max_2010_2014_passive_uk",
    "ford_c_max_2015_2019_keyed_uk",
    "ford_c_max_2015_2019_passive_uk",
    "ford_c_max_2010_2015_keyed_uk",
}

SOURCE_IDS = [
    "ford_official_pats_security_access_timed_delay",
    "ford_cmax_owner_manual_pats",
]

NOTE = (
    "Ford's official PATS service procedure uses timed security access before diagnostic key programming. "
    "Apply the timed PATS route to these UK C-Max records; this does not claim that every aftermarket tool "
    "uses the full wait, because some supported tools may calculate or bypass access internally."
)


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    items = data.get("items", {})
    changed = 0
    found = set()

    for record in items.values():
        if not isinstance(record, dict):
            continue
        record_id = record.get("record_id")
        if record_id not in TARGET_IDS:
            continue
        found.add(record_id)

        info = record.setdefault("vehicle_information", {})
        programming = info.setdefault("programming", {})
        if programming.get("security_access") != "timed_pats":
            programming["security_access"] = "timed_pats"
            changed += 1

        verification = record.setdefault("verification", {})
        sources = verification.setdefault("sources", [])
        for source_id in SOURCE_IDS:
            if source_id not in sources:
                sources.append(source_id)
        verification["security_access_status"] = "verified_from_official_ford_pats_procedure"
        verification["security_access_note"] = NOTE
        verification["last_checked"] = "2026-07-17"

    missing = sorted(TARGET_IDS - found)
    if missing:
        raise SystemExit(f"Missing expected C-Max records: {missing}")

    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Updated {changed} C-Max records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
