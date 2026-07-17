#!/usr/bin/env python3
"""Canonicalise known Ford security-access labels without inventing support.

This migration only converts existing human-readable labels into the controlled
vocabulary used by the Ford security-access audit. It does not infer routes for
records where the field is missing.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORD = ROOT / "database" / "vehicles" / "ford"

MAPPING = {
    "Exact-build verification required": "verification_required",
    "MQB49 5C / 5D operation-specific workflow": "vw_mqb49_5c_5d",
}


def update_record(record: dict[str, Any]) -> bool:
    containers: list[dict[str, Any]] = []

    security = record.get("security")
    if isinstance(security, dict):
        containers.append(security)

    info = record.get("vehicle_information")
    if isinstance(info, dict):
        containers.append(info)
        programming = info.get("programming")
        if isinstance(programming, dict):
            containers.append(programming)

    for container in containers:
        for key in ("security_access_method", "security_access"):
            value = container.get(key)
            if value in MAPPING:
                container[key] = MAPPING[value]
                return True
    return False


def main() -> int:
    files_changed = 0
    records_changed = 0

    for path in sorted(FORD.glob("*/models.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for record in data.get("items", {}).values():
            if isinstance(record, dict) and update_record(record):
                records_changed += 1
                changed = True
        if changed:
            path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            files_changed += 1

    print(json.dumps({"files_changed": files_changed, "records_changed": records_changed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
