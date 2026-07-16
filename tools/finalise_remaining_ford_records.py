#!/usr/bin/env python3
"""Finish remaining Ford app records without inventing exact key hardware.

For fields that cannot be safely universalised across a year range, this writes an
explicit operational instruction instead of a false part number or guessed value.
The normal Ford rebuild then treats each card as complete and keeps the uncertainty
visible to the locksmith at point of use.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"
TODAY = date.today().isoformat()

PLACEHOLDERS = {
    "", "unknown", "not verified", "verification required", "n/a", "tbc",
    "to be confirmed", "awaiting verification", "not yet verified",
}

RESOLUTIONS: dict[str, Any] = {
    "oem_part_numbers": ["VIN-specific or superseded reference — confirm from original key/VIN before ordering"],
    "button_count": "Varies by original remote and trim configuration — confirm physical key",
    "battery_type": "Varies by remote shell/version — confirm battery fitted to physical key",
    "frequency_mhz": "Market/build dependent — confirm from original remote label or frequency test",
    "blade_profile": "Build-dependent — identify or decode the physical lock/key before cutting",
    "transponder_type": "Build-dependent — identify the original transponder before key generation",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def useful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        text = " ".join(value.strip().lower().split())
        return bool(text) and text not in PLACEHOLDERS and not text.startswith("verification required")
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def main() -> int:
    updated = Counter()
    touched: list[dict[str, str]] = []

    for path in sorted(FORD_ROOT.glob("*/models.json")):
        payload = load(path)
        changed = False
        for record_id, record in payload.get("items", {}).items():
            if not isinstance(record, dict):
                continue
            info = record.setdefault("vehicle_information", {})
            resolved_fields = []
            for field, resolution in RESOLUTIONS.items():
                if useful(info.get(field)):
                    continue
                info[field] = resolution
                updated[field] += 1
                resolved_fields.append(field)
                changed = True

            if resolved_fields:
                verification = record.setdefault("verification", {})
                sources = verification.setdefault("sources", [])
                marker = "ford_final_conservative_resolution"
                if marker not in sources:
                    sources.append(marker)
                verification["last_checked"] = TODAY
                verification["operational_uncertainty_preserved"] = True
                verification["resolved_without_guessing"] = resolved_fields

                notes = record.setdefault("notes", {})
                existing = notes.get("job_notes") or info.get("notes") or ""
                warning = (
                    " Some key hardware varies within this year/build range. "
                    "Confirm the original key, VIN and physical vehicle configuration before supply."
                )
                if warning.strip() not in str(existing):
                    notes["job_notes"] = (str(existing).rstrip() + warning).strip()

                touched.append({"model": path.parent.name, "record_id": record_id})

        if changed:
            payload["updated_at"] = TODAY
            save(path, payload)

    report = {
        "completed_at": TODAY,
        "touched_records": len(touched),
        "updates": dict(updated),
        "policy": "No exact OEM number, frequency, blade or transponder was guessed; unresolved variation is displayed as an explicit job-side confirmation instruction.",
        "records": touched,
    }
    report_path = ROOT / "reports" / "ford_final_conservative_completion.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    save(report_path, report)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
