#!/usr/bin/env python3
"""Run the Ford rebuild and reliably publish its version/report.

This wrapper fixes the two practical gaps in the original rebuild workflow:
1. the root manifest stores Ford version under manufacturers.ford;
2. all referenced tool IDs must exist in the shared tools catalogue.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import rebuild_all_ford_records

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"
TOOLS_PATH = ROOT / "manufacturers" / "_shared" / "tools.json"
REPORT_PATH = ROOT / "reports" / "ford_full_rebuild_report.json"
TODAY = date.today().isoformat()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def bump_root_manifest() -> None:
    path = ROOT / "manifest.json"
    data = load(path)
    ford = data.setdefault("manufacturers", {}).setdefault("ford", {})
    ford["version"] = int(ford.get("version", 0)) + 1
    ford["status"] = "ford_full_record_rebuild"
    ford["updated_at"] = TODAY
    data["updated_at"] = TODAY
    save(path, data)


def validate_tool_ids() -> list[dict]:
    catalogue = load(TOOLS_PATH).get("tools", {})
    missing = []
    for path in sorted(FORD_ROOT.glob("*/models.json")):
        data = load(path)
        for record_id, record in data.get("items", {}).items():
            info = record.get("vehicle_information", {})
            for tool_id in info.get("tool_ids", []) or []:
                if tool_id not in catalogue:
                    missing.append({
                        "model": path.parent.name,
                        "record_id": record_id,
                        "tool_id": tool_id,
                    })
    return missing


def main() -> int:
    rebuild_all_ford_records.main()
    bump_root_manifest()

    report = load(REPORT_PATH)
    missing_tool_ids = validate_tool_ids()
    report["shared_tool_catalogue"] = {
        "path": str(TOOLS_PATH.relative_to(ROOT)),
        "missing_referenced_tool_ids": missing_tool_ids,
        "status": "pass" if not missing_tool_ids else "needs_mapping",
    }
    report["publication"] = {
        "root_manifest_ford_version_bumped": True,
        "published_at": TODAY,
    }
    save(REPORT_PATH, report)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if missing_tool_ids:
        raise SystemExit("Ford records reference tool IDs missing from manufacturers/_shared/tools.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
