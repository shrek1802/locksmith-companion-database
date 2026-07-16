#!/usr/bin/env python3
"""Audit Ford records for explicit security-access method.

The audit prevents 'OBD supported' from being treated as proof that security
access is available. Timed PATS, coded Incode/Outcode, tool-calculated access,
Ford online/FDRS, and VW-derived MQB/MEB access are separate routes.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORD = ROOT / "database" / "vehicles" / "ford"
OUTPUT = ROOT / "reports" / "ford_security_access_audit.json"

ALLOWED = {
    "none",
    "manual_key_cycle",
    "timed_pats",
    "coded_pats_incode_outcode",
    "tool_calculated_or_bypassed_pats",
    "ford_online_fdrs",
    "vw_mqb49_5c_5d",
    "vw_meb_authorised_online",
    "verification_required",
}


def iter_records() -> list[tuple[Path, str, dict[str, Any]]]:
    found = []
    for path in sorted(FORD.glob("*/models.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for key, record in data.get("items", {}).items():
            if isinstance(record, dict):
                found.append((path, key, record))
    return found


def extract(record: dict[str, Any]) -> str | None:
    security = record.get("security") or {}
    info = record.get("vehicle_information") or {}
    programming = info.get("programming") or {}
    value = (
        security.get("security_access_method")
        or security.get("security_access")
        or info.get("security_access_method")
        or info.get("security_access")
        or programming.get("security_access_method")
        or programming.get("security_access")
    )
    return str(value).strip() if value is not None else None


def main() -> int:
    missing = []
    invalid = []
    complete = []
    for path, item_key, record in iter_records():
        vehicle = record.get("vehicle") or {}
        method = extract(record)
        row = {
            "path": str(path.relative_to(ROOT)),
            "item_key": item_key,
            "record_id": record.get("record_id"),
            "model": vehicle.get("model"),
            "variant": vehicle.get("variant"),
            "year_from": vehicle.get("year_from"),
            "year_to": vehicle.get("year_to"),
            "security_access_method": method,
        }
        if not method:
            missing.append(row)
        elif method not in ALLOWED:
            invalid.append(row)
        else:
            complete.append(row)

    report = {
        "policy": "Programming route and security-access route must be recorded separately.",
        "allowed_methods": sorted(ALLOWED),
        "counts": {
            "records": len(missing) + len(invalid) + len(complete),
            "complete": len(complete),
            "missing": len(missing),
            "invalid": len(invalid),
        },
        "missing": missing,
        "invalid": invalid,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], indent=2))
    return 1 if invalid else 0


if __name__ == "__main__":
    raise SystemExit(main())
