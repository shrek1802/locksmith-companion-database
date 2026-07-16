#!/usr/bin/env python3
"""Restore explicit MQB49 classification for VW-derived UK Ford Connect models.

This deliberately does NOT claim tool support. It restores the security-platform
identity and creates operation slots that require evidence before the app can
show a tool as supported.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today().isoformat()
TARGETS = {
    "database/vehicles/ford/tourneo_connect/models.json": "tourneo_connect_2022_present_mqb",
    "database/vehicles/ford/transit_connect/models.json": "transit_connect_2024_present_mqb",
}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def verification_operation(summary: str) -> dict[str, Any]:
    return {
        "overall_status": "verification_required",
        "summary": summary,
        "programming_method": "VAG MQB49 workflow",
        "online_requirement": "Tool, key type, software version and vehicle build dependent",
        "tools": {},
        "evidence_required": [
            "official tool coverage for the exact operation",
            "exact 5C or 5D key identification",
            "working-key requirement",
            "SFD/online requirement",
            "required licence and adapter",
        ],
    }


def patch_record(record: dict[str, Any]) -> None:
    info = record.setdefault("vehicle_information", {})
    info["platform"] = "Volkswagen MQB49"
    info["immobiliser_system"] = "Volkswagen MQB49 security architecture"
    info["immobiliser_generation"] = "MQB49 5C / 5D — identify exact key type before accepting job"
    info["security_access"] = "MQB49 5C / 5D operation-specific workflow"
    info["programming_module"] = "VAG immobiliser / body-access system as fitted"
    info["tool_or_cable_required"] = "Operation-specific MQB49 licence, key-reading hardware and vehicle connection; verify exact tool workflow"
    info["notes"] = (
        "VW Caddy V-derived Ford application. Do not use Ford PATS/Incode-Outcode. "
        "Identify whether the original key is MQB49 5C or 5D before quoting. "
        "A tool being able to generate a remote does not prove it can read original-key data, "
        "prepare a dealer key, perform Add Key or complete AKL."
    )

    programming = info.setdefault("programming", {})
    programming.update({
        "route": "VAG MQB49 operation-specific workflow",
        "security_access": "MQB49 5C / 5D",
        "online_requirement": "Operation/build/tool dependent; verify SFD and online requirements",
        "read_original_key": "Required workflow stage where specified by the selected 5C/5D tool solution",
        "dealer_key_generation": "Requires operation-specific verified tool support",
        "add_key": "Verification required — do not infer support from a general vehicle tool list",
        "all_keys_lost": "Verification required — no AKL claim without exact evidence",
    })

    record["security"] = {
        **(record.get("security") if isinstance(record.get("security"), dict) else {}),
        "family": "Volkswagen MQB49",
        "platform": "Volkswagen MQB49",
        "generation": "MQB49 5C / 5D",
        "security_access": "MQB49 5C / 5D operation-specific workflow",
        "programming_route": "VAG MQB49 operation-specific workflow",
        "online_requirement": "Operation/build/tool dependent; verify SFD and online requirements",
        "ford_pats_incode_outcode": "Not applicable",
    }

    operations = record.setdefault("operations", {})
    operations["read_original_key"] = verification_operation(
        "Identify 5C/5D and use a tool with explicit original-key data-reading support."
    )
    operations["dealer_key_generation"] = verification_operation(
        "Requires verified MQB49 dealer-key preparation support for the exact key type."
    )
    operations["add_key"] = verification_operation(
        "Do not book until exact vehicle build, 5C/5D key type and tool workflow are confirmed."
    )
    operations["all_keys_lost"] = verification_operation(
        "No general AKL claim. Requires a separately verified exact-build solution."
    )

    tools = record.setdefault("tools", {})
    tools["supported_tools"] = []
    tools["tool_ids"] = []
    tools["compatibility_policy"] = "Operation-specific evidence only; general Ford or VAG compatibility is not sufficient."
    tools["programming_route"] = "VAG MQB49 operation-specific workflow"
    tools["online_requirement"] = "Operation/build/tool dependent; verify SFD and online requirements"

    verification = record.setdefault("verification", {})
    verification["last_checked"] = TODAY
    verification["status"] = "mqb49_platform_restored_tool_matrix_pending"
    verification["platform_restored"] = True
    verification["tool_claims_quarantined"] = True
    sources = verification.setdefault("sources", [])
    if "ford_mqb49_platform_restore" not in sources:
        sources.append("ford_mqb49_platform_restore")

    record["record_completion"] = {
        "status": "needs_targeted_verification",
        "missing_fields": [
            "mqb49_exact_5c_or_5d",
            "operations.read_original_key.tools",
            "operations.dealer_key_generation.tools",
            "operations.add_key.tools",
            "operations.all_keys_lost.tools",
            "sfd_requirement",
            "working_key_requirement",
        ],
        "rebuilt_at": TODAY,
        "pipeline": "restore_ford_mqb49_platforms_v1",
    }


def main() -> int:
    changed: list[dict[str, str]] = []
    for rel_path, record_id in TARGETS.items():
        path = ROOT / rel_path
        payload = load(path)
        record = payload.get("items", {}).get(record_id)
        if not isinstance(record, dict):
            raise RuntimeError(f"Missing target record: {rel_path}:{record_id}")
        patch_record(record)
        payload["updated_at"] = TODAY
        save(path, payload)
        changed.append({"path": rel_path, "record_id": record_id})

    report = {
        "generated_at": TODAY,
        "changed_records": changed,
        "platform": "Volkswagen MQB49",
        "security_families": ["MQB49 5C", "MQB49 5D"],
        "tool_support_claimed": False,
        "policy": "Tool support remains blocked until operation-specific evidence is entered.",
    }
    save(ROOT / "reports" / "ford_mqb49_restore_report.json", report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
