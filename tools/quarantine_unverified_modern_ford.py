#!/usr/bin/env python3
"""Quarantine unsafe modern-Ford tool claims without deleting verified key data.

This is a safety pass for the app. It preserves vehicle/key/OEM/platform fields, but
removes generic record-level programmer claims from modern/restricted Ford records
unless an operation has an explicit evidence-backed tool matrix.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"
TODAY = date.today().isoformat()

RESTRICTED_MARKERS = (
    "mqb", "mqb49", "5c", "5d", "meb", "fdrs", "can fd", "can-fd",
    "doip", "sfd", "hitag aes", "secure gateway", "online security",
)
GENERATION_ONLY_IDS = {
    "autel_km100x", "xhorse_key_tool_max_pro", "keydiy_kd_x4", "keydiy_kd_max",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def text_blob(record: dict[str, Any]) -> str:
    vehicle = record.get("vehicle", {})
    info = record.get("vehicle_information", {})
    programming = info.get("programming", {}) if isinstance(info.get("programming"), dict) else {}
    values = [
        vehicle.get("generation"), vehicle.get("variant"),
        info.get("immobiliser_system"), info.get("immobiliser_generation"),
        info.get("transponder_type"), info.get("platform"), info.get("security_access"),
        programming.get("route"), programming.get("online_requirement"), info.get("notes"),
    ]
    return " ".join(str(v) for v in values if v is not None).lower()


def is_restricted(record: dict[str, Any]) -> bool:
    vehicle = record.get("vehicle", {})
    year_from = int(vehicle.get("year_from") or 0)
    blob = text_blob(record)
    return year_from >= 2022 or any(marker in blob for marker in RESTRICTED_MARKERS)


def explicit_evidence_tool_map(operation: Any) -> dict[str, Any]:
    if not isinstance(operation, dict):
        return {}
    tools = operation.get("tools")
    if not isinstance(tools, dict):
        return {}
    verified: dict[str, Any] = {}
    for tool_id, value in tools.items():
        if not isinstance(value, dict):
            continue
        status = str(value.get("status") or "").lower()
        sources = value.get("sources") or value.get("evidence") or value.get("source_ids")
        if status in {"supported", "partially_supported", "conditional"} and sources:
            verified[tool_id] = value
    return verified


def quarantine_operation(record: dict[str, Any], operation_id: str) -> bool:
    operations = record.setdefault("operations", {})
    raw = operations.get(operation_id)
    existing = raw if isinstance(raw, dict) else {}
    verified_tools = explicit_evidence_tool_map(existing)
    changed = False

    if verified_tools:
        if existing.get("tools") != verified_tools:
            existing["tools"] = verified_tools
            changed = True
        operations[operation_id] = existing
        return changed

    safe = {
        "overall_status": "verification_required",
        "method": "Do not accept this job from model/year alone. Confirm the exact build, security platform and current tool coverage before booking.",
        "method_text": "Exact-build and operation-specific verification required",
        "programming_method": existing.get("programming_method") or existing.get("route") or "Restricted diagnostic/online workflow — verify exact build",
        "online_requirement": existing.get("online_requirement") or "Operation and build dependent",
        "tools": {},
        "job_acceptance": "DO_NOT_CONFIRM_UNTIL_TOOL_MENU_OR_PRIMARY_COVERAGE_IS_VERIFIED",
    }
    if existing != safe:
        operations[operation_id] = safe
        changed = True
    return changed


def main() -> int:
    touched_records = 0
    removed_programmer_claims = 0
    preserved_generation_tools = 0
    quarantined_operations = 0
    affected: list[dict[str, Any]] = []

    for path in sorted(FORD_ROOT.glob("*/models.json")):
        payload = load(path)
        file_changed = False
        for record_id, record in payload.get("items", {}).items():
            if not isinstance(record, dict) or not is_restricted(record):
                continue

            changed = False
            info = record.setdefault("vehicle_information", {})
            top_tools = record.setdefault("tools", {}) if isinstance(record.get("tools"), dict) else {}
            record["tools"] = top_tools

            old_ids = []
            for value in (info.get("tool_ids"), top_tools.get("tool_ids")):
                if isinstance(value, list):
                    old_ids.extend(str(v) for v in value)
            supported = top_tools.get("supported_tools")
            if isinstance(supported, list):
                old_ids.extend(str(item.get("id")) for item in supported if isinstance(item, dict) and item.get("id"))

            candidates = sorted(set(old_ids))
            generation = sorted(set(
                [str(v) for v in info.get("generation_tool_ids", []) if v] +
                [tool_id for tool_id in candidates if tool_id in GENERATION_ONLY_IDS]
            ))
            programmer_candidates = [tool_id for tool_id in candidates if tool_id not in GENERATION_ONLY_IDS]

            if programmer_candidates:
                info["unverified_programmer_candidates"] = programmer_candidates
                removed_programmer_claims += len(programmer_candidates)
                changed = True
            if generation:
                info["generation_tool_ids"] = generation
                preserved_generation_tools += len(generation)

            if info.get("tool_ids"):
                info["tool_ids"] = []
                changed = True
            if top_tools.get("tool_ids"):
                top_tools["tool_ids"] = []
                changed = True
            if top_tools.get("supported_tools"):
                top_tools["supported_tools"] = []
                changed = True

            top_tools["Important"] = (
                "No programmer is confirmed by model/year alone for this restricted record. "
                "Use the operation-specific matrix only; verify current software, exact build and required online access."
            )
            top_tools["job_acceptance"] = "verification_required"

            for operation_id in ("add_key", "all_keys_lost"):
                if quarantine_operation(record, operation_id):
                    quarantined_operations += 1
                    changed = True

            programming = info.setdefault("programming", {}) if isinstance(info.get("programming"), dict) else {}
            info["programming"] = programming
            programming["add_key"] = "Verification required — operation-specific tool evidence missing"
            programming["all_keys_lost"] = "Verification required — operation-specific tool evidence missing"
            programming.setdefault("online_requirement", "Operation and build dependent")

            security = record.setdefault("security", {}) if isinstance(record.get("security"), dict) else {}
            record["security"] = security
            security.setdefault("security_access", info.get("security_access") or programming.get("security_access") or "Exact-build verification required")
            security["job_acceptance"] = "verification_required"

            completion = record.setdefault("record_completion", {})
            completion["status"] = "needs_targeted_verification"
            missing = set(completion.get("missing_fields") or [])
            missing.update({"operations.add_key.tools", "operations.all_keys_lost.tools", "security_access"})
            completion["missing_fields"] = sorted(missing)
            completion["safety_quarantined_at"] = TODAY

            verification = record.setdefault("verification", {})
            verification["modern_tool_claims_quarantined"] = True
            verification["last_checked"] = TODAY

            if changed:
                touched_records += 1
                file_changed = True
                vehicle = record.get("vehicle", {})
                affected.append({
                    "model_folder": path.parent.name,
                    "record_id": record_id,
                    "model": vehicle.get("model"),
                    "variant": vehicle.get("variant"),
                    "year_from": vehicle.get("year_from"),
                    "year_to": vehicle.get("year_to"),
                    "platform_text": text_blob(record)[:300],
                    "unverified_programmer_candidates": programmer_candidates,
                })

        if file_changed:
            payload["updated_at"] = TODAY
            save(path, payload)

    report = {
        "generated_at": TODAY,
        "touched_records": touched_records,
        "removed_programmer_claims": removed_programmer_claims,
        "preserved_generation_tool_references": preserved_generation_tools,
        "quarantined_operations": quarantined_operations,
        "policy": "Modern/restricted Ford support must be operation-specific and evidence-backed.",
        "affected": affected,
    }
    report_path = ROOT / "reports" / "ford_modern_safety_quarantine.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    save(report_path, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
