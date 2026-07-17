#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORD = ROOT / "database" / "vehicles" / "ford"
REPORT = ROOT / "reports" / "ford_true_completion_audit.json"

PLACEHOLDERS = {
    None,
    "",
    "verification_required",
    "research_required",
    "unknown",
    "tbc",
    "todo",
}


def main():
    records = []
    incomplete = []
    parse_errors = []

    for path in sorted(FORD.glob("*/models.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            parse_errors.append({"path": str(path.relative_to(ROOT)), "error": str(exc)})
            continue

        items = data.get("items")
        if not isinstance(items, dict):
            parse_errors.append({
                "path": str(path.relative_to(ROOT)),
                "error": "models.json has no top-level items object",
            })
            continue

        for item_key, record in items.items():
            if not isinstance(record, dict):
                continue

            records.append(record)
            vehicle = record.get("vehicle") if isinstance(record.get("vehicle"), dict) else {}
            vehicle_info = record.get("vehicle_information") if isinstance(record.get("vehicle_information"), dict) else {}
            programming = vehicle_info.get("programming") if isinstance(vehicle_info.get("programming"), dict) else {}
            security = programming.get("security_access")
            normalized = security.strip().lower() if isinstance(security, str) else security

            if normalized in PLACEHOLDERS:
                incomplete.append({
                    "path": str(path.relative_to(ROOT)),
                    "item_key": item_key,
                    "record_id": record.get("record_id"),
                    "model": vehicle.get("model"),
                    "variant": vehicle.get("variant"),
                    "year_from": vehicle.get("year_from"),
                    "year_to": vehicle.get("year_to"),
                    "security_access": security,
                })

    report = {
        "policy": "Ford is complete only when every vehicle record has a verified, non-placeholder vehicle_information.programming.security_access value.",
        "counts": {
            "records": len(records),
            "fully_verified": len(records) - len(incomplete),
            "incomplete": len(incomplete),
            "parse_errors": len(parse_errors),
        },
        "incomplete": incomplete,
        "parse_errors": parse_errors,
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], indent=2))
    return 1 if incomplete or parse_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
