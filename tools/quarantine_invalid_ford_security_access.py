#!/usr/bin/env python3
"""Quarantine invalid Ford security-access identifiers without losing their text."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "ford_security_access_audit.json"
QUEUE = ROOT / "reports" / "ford_security_access_research_queue_2026_07_18.json"


def main() -> int:
    audit = json.loads(REPORT.read_text(encoding="utf-8"))
    if not audit.get("invalid") and QUEUE.exists():
        existing = json.loads(QUEUE.read_text(encoding="utf-8"))
        if isinstance(existing.get("items"), list):
            existing["items"] = {item["record_id"]: item for item in existing["items"]}
            QUEUE.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("no invalid identifiers remain; normalised existing research queue")
        return 0
    queue = []
    changed_files: set[Path] = set()
    documents: dict[Path, dict] = {}

    for issue in audit.get("invalid", []):
        path = ROOT / issue["path"]
        document = documents.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
        item = document["items"][issue["item_key"]]
        programming = item["vehicle_information"]["programming"]
        previous = programming["security_access"]
        programming["security_access"] = "verification_required"
        programming["security_access_previous_unvalidated"] = previous
        programming["security_access_status"] = "research_required"
        programming["security_access_note"] = (
            "Previous method identifier was not accepted by the Ford security-access validator and lacked "
            "record-level evidence. It is retained above as a research lead, not as a verified route."
        )
        queue.append({
            "path": issue["path"].replace("\\", "/"),
            "item_key": issue["item_key"],
            "record_id": issue["record_id"],
            "model": issue["model"],
            "variant": issue["variant"],
            "year_from": issue["year_from"],
            "year_to": issue["year_to"],
            "previous_unvalidated_method": previous,
            "evidence_needed": [
                "Exact Ford or tool-vendor model/year security-access coverage",
                "Separate Add Key and All Keys Lost authorization requirements",
                "Confirmation of timed PATS, coded incode/outcode, tool-calculated bypass or Ford online FDRS route",
            ],
        })
        changed_files.add(path)

    for path in sorted(changed_files):
        path.write_text(json.dumps(documents[path], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    result = {
        "schema_version": "1.0",
        "generated_at": "2026-07-18",
        "manufacturer": "Ford",
        "market": "UK",
        "drive_side": "RHD",
        "count": len(queue),
        "items": {item["record_id"]: item for item in queue},
    }
    QUEUE.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"quarantined {len(queue)} invalid security-access identifiers in {len(changed_files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
