#!/usr/bin/env python3
"""Build evidence-first Ford research batches from the modern safety quarantine.

This script does not claim tool support. It converts quarantined records into a
repeatable research queue grouped by security architecture and requires separate
evidence for each operation/tool combination.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
QUARANTINE = ROOT / "reports" / "ford_modern_safety_quarantine.json"
OUTPUT = ROOT / "reports" / "ford_operation_research_queue.json"

OPERATIONS = [
    "identify_original_key",
    "read_original_key",
    "dealer_key_generation",
    "add_key",
    "all_keys_lost",
    "parameter_reset",
]


def classify(text: str) -> str:
    value = text.lower()
    if "mqb49" in value or "mqb-derived" in value or "caddy v" in value:
        return "vw_mqb49_5c_5d"
    if "meb" in value:
        return "vw_meb_derived"
    if "fdrs" in value or "connected security" in value or "can-fd" in value or "secure gateway" in value:
        return "ford_connected_fdrs_or_secured"
    if "hitag aes" in value or "id49" in value:
        return "ford_hitag_aes"
    if "hitag pro" in value or "pcf7939" in value or "id47" in value:
        return "ford_hitag_pro"
    if "4d" in value or "dst80" in value or "id63" in value:
        return "ford_pats_4d_dst80"
    return "ford_platform_unresolved"


def evidence_template() -> dict[str, Any]:
    return {
        "status": "verification_required",
        "tools": {},
        "evidence_requirements": [
            "Exact model, generation, ignition type and UK/RHD applicability",
            "Exact operation named by the tool manufacturer",
            "Current software version or dated release note",
            "Required licence/subscription, adapter, cable or online account",
            "Working-key requirement and AKL limitations",
            "Primary source URL/document plus access date",
        ],
    }


def main() -> int:
    if not QUARANTINE.exists():
        raise SystemExit(f"Missing {QUARANTINE}; run the Ford safety quarantine workflow first.")

    source = json.loads(QUARANTINE.read_text(encoding="utf-8"))
    batches: dict[str, list[dict[str, Any]]] = {}

    for item in source.get("affected", []):
        platform = classify(str(item.get("platform_text", "")))
        record = {
            "model_folder": item.get("model_folder"),
            "record_id": item.get("record_id"),
            "model": item.get("model"),
            "variant": item.get("variant"),
            "year_from": item.get("year_from"),
            "year_to": item.get("year_to"),
            "security_platform": platform,
            "candidate_tools_removed_from_general_claims": item.get("unverified_programmer_candidates", []),
            "operations": {operation: evidence_template() for operation in OPERATIONS},
            "job_acceptance": {
                "status": "do_not_confirm_until_operation_verified",
                "required_customer_details": [
                    "VIN",
                    "registration/build date",
                    "keyed or passive ignition",
                    "working key available",
                    "requested operation",
                ],
            },
        }
        batches.setdefault(platform, []).append(record)

    priority = [
        "vw_mqb49_5c_5d",
        "ford_connected_fdrs_or_secured",
        "ford_hitag_aes",
        "ford_hitag_pro",
        "ford_pats_4d_dst80",
        "vw_meb_derived",
        "ford_platform_unresolved",
    ]
    ordered = {name: batches.get(name, []) for name in priority if batches.get(name)}

    output = {
        "generated_from": str(QUARANTINE.relative_to(ROOT)),
        "policy": "A vehicle-level tool listing never proves operation support.",
        "status_meanings": {
            "supported": "Primary evidence proves the exact operation for the exact application.",
            "conditional": "Primary evidence proves support with explicit conditions shown in the record.",
            "not_supported": "Primary evidence explicitly excludes the operation/application.",
            "verification_required": "No sufficiently precise primary evidence has been recorded.",
        },
        "batch_counts": {name: len(records) for name, records in ordered.items()},
        "batches": ordered,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output["batch_counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
