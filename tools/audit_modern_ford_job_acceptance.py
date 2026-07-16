#!/usr/bin/env python3
"""Audit modern Ford records for unsafe job-acceptance claims.

This validator is deliberately strict. A modern/restricted Ford record may list
record-level tools, but Add Key and AKL support must be explicit per operation.
It also blocks generic OEM placeholders from being treated as verified numbers
and checks that shared VW-platform vehicles identify MQB/MEB security clearly.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORD = ROOT / "database" / "vehicles" / "ford"
REPORT = ROOT / "reports" / "modern_ford_job_acceptance_audit.json"

PLACEHOLDER_TERMS = (
    "vin-specific or superseded reference",
    "confirm from original key",
    "confirm from original key/vin",
    "verification required",
    "exact application verification required",
    "market/build dependent",
)
RESTRICTED_TERMS = (
    "mqb49", "mqb", "meb", "fdrs", "can fd", "can-fd", "doip", "sfd",
    "volkswagen", "authorised online", "online security",
)


def useful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        text = value.strip().lower()
        return bool(text) and not any(term in text for term in PLACEHOLDER_TERMS)
    if isinstance(value, list):
        return bool(value) and any(useful(item) for item in value)
    if isinstance(value, dict):
        return bool(value) and any(useful(item) for item in value.values())
    return True


def restricted(record: dict[str, Any]) -> bool:
    vehicle = record.get("vehicle", {})
    info = record.get("vehicle_information", {})
    year = int(vehicle.get("year_from") or 0)
    text = " ".join(str(value) for value in (
        vehicle.get("generation"), vehicle.get("variant"),
        info.get("immobiliser_system"), info.get("immobiliser_generation"),
        info.get("platform"), info.get("transponder_type"),
        (info.get("programming") or {}).get("route"),
        (info.get("programming") or {}).get("online_requirement"),
        info.get("security_access"),
    ) if value).lower()
    return year >= 2022 or any(term in text for term in RESTRICTED_TERMS)


def operation(record: dict[str, Any], name: str) -> dict[str, Any]:
    value = (record.get("operations") or {}).get(name)
    if isinstance(value, dict):
        return value
    value = ((record.get("vehicle_information") or {}).get("programming") or {}).get(name)
    return value if isinstance(value, dict) else {}


def main() -> int:
    failures: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    checked = 0

    for path in sorted(FORD.glob("*/models.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        for record_id, record in (payload.get("items") or {}).items():
            if not isinstance(record, dict) or not restricted(record):
                continue
            checked += 1
            vehicle = record.get("vehicle", {})
            info = record.get("vehicle_information", {})
            context = {
                "model_folder": path.parent.name,
                "record_id": record_id,
                "model": vehicle.get("model"),
                "variant": vehicle.get("variant"),
                "year_from": vehicle.get("year_from"),
                "year_to": vehicle.get("year_to"),
            }

            security_text = " ".join(str(info.get(k) or "") for k in (
                "immobiliser_system", "immobiliser_generation", "platform", "transponder_type"
            )).lower()
            generation_text = str(vehicle.get("generation") or "").lower()
            if "volkswagen" in security_text or "caddy" in generation_text:
                if not any(term in security_text for term in ("mqb49c", "mqb49d", "mqb", "meb")):
                    failures.append({**context, "issue": "VW-derived Ford lacks an explicit MQB/MEB security classification"})

            for op_name in ("add_key", "all_keys_lost"):
                op = operation(record, op_name)
                tools = op.get("tools") if isinstance(op, dict) else None
                status = str(op.get("status") or op.get("overall_status") or "").lower() if isinstance(op, dict) else ""
                if not isinstance(tools, dict) or not tools:
                    failures.append({**context, "operation": op_name, "issue": "No explicit operation-level tool matrix"})
                if status == "supported" and (not isinstance(tools, dict) or not tools):
                    failures.append({**context, "operation": op_name, "issue": "Operation marked supported without explicit tools"})

            oem = info.get("oem_part_numbers")
            if not useful(oem):
                warnings.append({**context, "issue": "OEM key number is unverified/placeholder and must not be presented as a verified part number"})

            access = info.get("security_access") or (info.get("programming") or {}).get("security_access")
            online = info.get("online_requirement") or (info.get("programming") or {}).get("online_requirement")
            if not useful(access) and not useful(online):
                warnings.append({**context, "issue": "Security access/online requirement not explicitly defined"})

    result = {
        "checked_restricted_records": checked,
        "failures": len(failures),
        "warnings": len(warnings),
        "failure_items": failures,
        "warning_items": warnings,
        "policy": "Modern Ford job acceptance requires explicit operation-level tool support; record-level tool lists are informational only.",
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
