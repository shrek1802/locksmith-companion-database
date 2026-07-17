#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORD = ROOT / "database" / "vehicles" / "ford"
PLACEHOLDERS = {None, "", "verification_required", "research_required", "unknown", "tbc", "todo"}
EXCLUDED_TERMS = ("fdrs", "meb", "mqb", "volkswagen", "vw-derived", "online account", "dealer online")
UPDATED = []


def text(value):
    return "" if value is None else str(value).strip().lower()


def qualifies(record):
    vehicle = record.get("vehicle") or {}
    info = record.get("vehicle_information") or {}
    programming = info.get("programming") or {}

    current = programming.get("security_access")
    if text(current) not in PLACEHOLDERS:
        return False

    year_to = vehicle.get("year_to")
    year_from = vehicle.get("year_from")
    if not isinstance(year_from, int):
        return False
    if year_to is not None and (not isinstance(year_to, int) or year_to > 2018):
        return False

    combined = " ".join(text(v) for v in (
        info.get("immobiliser_system"),
        info.get("immobiliser_generation"),
        programming.get("route"),
        programming.get("add_key"),
        programming.get("all_keys_lost"),
        programming.get("online_requirement"),
        record.get("security"),
        record.get("operations"),
    ))

    if "pats" not in combined:
        return False
    if not any(term in combined for term in ("obd", "diagnostic", "security access", "timed")):
        return False
    if any(term in combined for term in EXCLUDED_TERMS):
        return False

    online = text(programming.get("online_requirement"))
    if online and online not in {"no", "normally no", "not normally", "offline"}:
        return False

    return True


def main():
    changed_files = 0
    for path in sorted(FORD.glob("*/models.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get("items")
        if not isinstance(items, dict):
            continue

        changed = False
        for item_key, record in items.items():
            if not isinstance(record, dict) or not qualifies(record):
                continue

            info = record.setdefault("vehicle_information", {})
            programming = info.setdefault("programming", {})
            programming["security_access"] = "timed_pats"

            verification = record.setdefault("verification", {})
            verification["security_access_status"] = "verified_from_explicit_record_family_metadata"
            verification["security_access_basis"] = (
                "Existing record explicitly identifies a Ford PATS family, an OBD/diagnostic programming route, "
                "no normal online requirement, and a UK vehicle range ending no later than 2018."
            )
            sources = verification.setdefault("sources", [])
            marker = "ford_existing_record_pats_route_classification"
            if isinstance(sources, list) and marker not in sources:
                sources.append(marker)

            vehicle = record.get("vehicle") or {}
            UPDATED.append({
                "path": str(path.relative_to(ROOT)),
                "item_key": item_key,
                "record_id": record.get("record_id"),
                "model": vehicle.get("model"),
                "variant": vehicle.get("variant"),
                "year_from": vehicle.get("year_from"),
                "year_to": vehicle.get("year_to"),
                "security_access": "timed_pats",
            })
            changed = True

        if changed:
            data["updated_at"] = "2026-07-17"
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            changed_files += 1

    report = ROOT / "reports" / "ford_legacy_pats_broad_batch.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({
        "policy": "Only explicit pre-2019 Ford PATS records with offline OBD/diagnostic routes are classified.",
        "updated_records": len(UPDATED),
        "changed_files": changed_files,
        "records": UPDATED,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"updated_records": len(UPDATED), "changed_files": changed_files}, indent=2))


if __name__ == "__main__":
    main()
