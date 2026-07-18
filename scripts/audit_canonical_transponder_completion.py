#!/usr/bin/env python3
"""Audit distinct UK vehicle/key records after canonical transponder mapping."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UNCERTAIN = re.compile(r"unknown|research|required|confirm|likely|var(?:y|ies|iant)|tbc|tbd|not recorded|unspecified|build-dependent", re.I)


def concrete(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not UNCERTAIN.search(value)


def main() -> None:
    catalogue = json.loads((ROOT / "database/reference/uk_transponder_catalogue.json").read_text(encoding="utf-8"))
    records = []
    for path in sorted((ROOT / "database/vehicles").glob("*/*/models.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for key, record in data.get("items", {}).items():
            info = record.get("vehicle_information", {})
            verification = info.get("transponder_verification", {})
            status = verification.get("status") if isinstance(verification, dict) else None
            has_value = concrete(info.get("transponder_type")) or concrete(info.get("transponder_id"))
            classification = "verified" if status == "verified" else "partially_verified" if has_value else "research_required"
            vehicle = record.get("vehicle", {})
            records.append({
                "record_id": record.get("record_id") or key,
                "manufacturer": vehicle.get("make") or data.get("manufacturer", {}).get("name"),
                "model": vehicle.get("model") or data.get("model", {}).get("name"),
                "variant": vehicle.get("variant"), "year_from": vehicle.get("year_from"), "year_to": vehicle.get("year_to"),
                "transponder_type": info.get("transponder_type"), "transponder_id": info.get("transponder_id"),
                "classification": classification, "model_file": str(path.relative_to(ROOT)).replace("\\", "/"),
            })
    counts = {name: sum(x["classification"] == name for x in records) for name in ("verified", "partially_verified", "research_required")}
    complete = counts["verified"] + counts["partially_verified"]
    catalogue_counts = {
        "canonical_families": len(catalogue["items"]),
        "supported_families": sum(x["status"] == "catalogue_supported" for x in catalogue["items"].values()),
        "research_required_families": sorted(k for k, x in catalogue["items"].items() if x["status"] != "catalogue_supported"),
    }
    report = {
        "schema_version": "2.1", "updated_at": "2026-07-18", "category": "canonical_transponder_completion_audit",
        "scope": "Distinct UK vehicle/key records in database/vehicles",
        "summary": {"total_records": len(records), **counts, "completion_percentage": round(100 * complete / len(records), 2) if records else 0},
        "catalogue": catalogue_counts,
        "unresolved_records": [x for x in records if x["classification"] == "research_required"],
    }
    output = ROOT / "reports/canonical_transponder_completion_audit.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"]))
    print(json.dumps(catalogue_counts))


if __name__ == "__main__":
    main()
