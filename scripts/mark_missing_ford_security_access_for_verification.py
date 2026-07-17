#!/usr/bin/env python3
"""Mark missing Ford security-access routes as verification_required.

This migration does not infer or claim a programming route. It only replaces a
missing value with the canonical explicit state used by the database when the
exact UK-market security-access route still requires evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORD = ROOT / "database" / "vehicles" / "ford"


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
    changed_files = 0
    changed_records = 0

    for path in sorted(FORD.glob("*/models.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        file_changed = False

        for record in data.get("items", {}).values():
            if not isinstance(record, dict) or extract(record):
                continue

            info = record.setdefault("vehicle_information", {})
            programming = info.setdefault("programming", {})
            programming["security_access"] = "verification_required"
            file_changed = True
            changed_records += 1

        if file_changed:
            path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            changed_files += 1

    print(json.dumps({"changed_files": changed_files, "changed_records": changed_records}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
