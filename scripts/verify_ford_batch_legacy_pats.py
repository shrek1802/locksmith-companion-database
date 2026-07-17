#!/usr/bin/env python3
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORD = ROOT / "database" / "vehicles" / "ford"

# Batch several UK Ford families in one controlled pass. The migration only
# touches records already describing an offline Ford PATS OBD route. It skips
# FDRS, MEB, VW-derived and any non-PATS/ambiguous record.
TARGET_FAMILIES = {
    "fiesta",
    "focus",
    "mondeo",
    "kuga",
    "galaxy",
    "s_max",
}

PLACEHOLDERS = {None, "", "verification_required", "research_required", "unknown", "tbc", "todo"}
SOURCE_ID = "ford_oem_pats_timed_security_access_procedure"
NOTE = (
    "Verified as the Ford OEM timed PATS security-access family because this record already identifies "
    "an offline Ford PATS OBD programming route. Compatible aftermarket tools may calculate, bypass or "
    "hide the wait internally; that tool behaviour does not change the underlying OEM access family."
)


def norm(value):
    return value.strip().lower() if isinstance(value, str) else value


def qualifies(item):
    vi = item.get("vehicle_information")
    if not isinstance(vi, dict):
        return False
    programming = vi.get("programming")
    if not isinstance(programming, dict):
        return False

    current = norm(programming.get("security_access"))
    if current not in PLACEHOLDERS:
        return False

    immo = " ".join(
        str(vi.get(key, ""))
        for key in ("immobiliser_system", "immobiliser_generation", "transponder_type")
    ).lower()
    route = str(programming.get("route", "")).lower()
    online = str(programming.get("online_requirement", "")).strip().lower()

    if "pats" not in immo:
        return False
    if "obd" not in route and "diagnostic" not in route:
        return False
    if online not in {"no", "normally no"}:
        return False
    if any(blocked in immo or blocked in route for blocked in ("fdrs", "meb", "mqb", "volkswagen", "vw ")):
        return False
    return True


def main():
    changed_files = []
    changed_records = []

    for family in sorted(TARGET_FAMILIES):
        path = FORD / family / "models.json"
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("items", {})
        file_changed = False

        for item_key, item in items.items():
            if not isinstance(item, dict) or not qualifies(item):
                continue

            programming = item["vehicle_information"]["programming"]
            programming["security_access"] = "timed_pats"

            verification = item.setdefault("verification", {})
            sources = verification.setdefault("sources", [])
            if SOURCE_ID not in sources:
                sources.append(SOURCE_ID)
            verification["last_checked"] = date.today().isoformat()
            verification["security_access_status"] = "verified_oem_family_route"
            verification["security_access_note"] = NOTE

            changed_records.append({
                "family": family,
                "item_key": item_key,
                "record_id": item.get("record_id"),
                "method": "timed_pats",
            })
            file_changed = True

        if file_changed:
            data["updated_at"] = date.today().isoformat()
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            changed_files.append(str(path.relative_to(ROOT)))

    print(json.dumps({
        "changed_files": changed_files,
        "changed_record_count": len(changed_records),
        "changed_records": changed_records,
    }, indent=2))

    if not changed_records:
        raise SystemExit("No qualifying Ford records were changed")


if __name__ == "__main__":
    main()
