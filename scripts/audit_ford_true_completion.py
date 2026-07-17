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

REQUIRED_RECORD_FIELDS = [
    ("security_access",),
]


def iter_records(data):
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and any(k in value for k in ("record_id", "model", "variant", "year_from")):
                yield key, value
            yield from iter_records(value)
    elif isinstance(data, list):
        for idx, value in enumerate(data):
            if isinstance(value, dict) and any(k in value for k in ("record_id", "model", "variant", "year_from")):
                yield str(idx), value
            yield from iter_records(value)


def get_nested(record, path):
    cur = record
    for part in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def main():
    records = []
    incomplete = []

    for path in sorted(FORD.glob("*/models.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            incomplete.append({"path": str(path.relative_to(ROOT)), "error": str(exc)})
            continue

        seen = set()
        for item_key, record in iter_records(data):
            rid = record.get("record_id") or f"{path.stem}:{item_key}"
            marker = (str(path), rid)
            if marker in seen:
                continue
            seen.add(marker)
            records.append(record)

            failures = []
            security = record.get("security_access")
            if security is None and isinstance(record.get("operations"), dict):
                security = record["operations"].get("security_access")
            if security is None and isinstance(record.get("programming"), dict):
                security = record["programming"].get("security_access")

            normalized = security.strip().lower() if isinstance(security, str) else security
            if normalized in PLACEHOLDERS:
                failures.append({"field": "security_access", "value": security})

            if failures:
                incomplete.append({
                    "path": str(path.relative_to(ROOT)),
                    "item_key": item_key,
                    "record_id": record.get("record_id"),
                    "model": record.get("model"),
                    "variant": record.get("variant"),
                    "year_from": record.get("year_from"),
                    "year_to": record.get("year_to"),
                    "failures": failures,
                })

    report = {
        "policy": "Ford is complete only when no record uses verification/research placeholders for security access.",
        "counts": {
            "records": len(records),
            "fully_verified": len(records) - len(incomplete),
            "incomplete": len(incomplete),
        },
        "incomplete": incomplete,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], indent=2))
    return 1 if incomplete else 0


if __name__ == "__main__":
    raise SystemExit(main())
