#!/usr/bin/env python3
"""Apply a Silca canonical transponder family to exact keyed records only."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "database" / "reference" / "uk_transponder_catalogue.json"
UNCERTAIN = re.compile(r"unknown|research|required|confirm|likely|var(?:y|ies|iant)|tbc|tbd|not recorded|unspecified", re.I)
PROXIMITY = re.compile(r"proximity|passive|keyless|smart key|kessy", re.I)
KEYED = re.compile(r"keyed|ignition key|transponder key|remote key|flip key|mechanical", re.I)
SLOT = re.compile(r"slot|dash key|fobik", re.I)


def concrete(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not UNCERTAIN.search(value)


def record_years(record: dict) -> tuple[int, int] | None:
    vehicle = record.get("vehicle", {})
    start, end = vehicle.get("year_from"), vehicle.get("year_to")
    if isinstance(start, int):
        return start, end if isinstance(end, int) else 2026
    years = [int(x) for x in re.findall(r"(?:19|20)\d{2}", str(record.get("years", "")))]
    if not years:
        return None
    return years[0], years[1] if len(years) > 1 else years[0]


def record_scope(record: dict) -> str:
    vehicle = record.get("vehicle", {})
    info = record.get("vehicle_information", record)
    text = " ".join(str(x) for x in (vehicle.get("variant"), info.get("key_type"), record.get("name")) if x)
    if PROXIMITY.search(text):
        return "proximity_emergency_insert"
    if SLOT.search(text):
        return "slot_key"
    if KEYED.search(text):
        return "keyed_or_remote_transponder_key"
    return "unknown"


def scope_matches(record: dict, app_scope: str) -> bool:
    scope = record_scope(record)
    if app_scope == "remote_or_flip_key":
        return scope == "keyed_or_remote_transponder_key"
    return scope == app_scope


def app_end(app: dict) -> int:
    if isinstance(app.get("year_to"), int):
        return app["year_to"]
    return 2025 if app["source_id"] == "silca_proximity_slot_remote_2025" else 2014


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    family_id = args.family.lower()
    family = catalogue["items"].get(family_id)
    if not family or family["status"] != "catalogue_supported":
        raise SystemExit(f"Unknown or unresolved family: {family_id}")
    applications_by_file: dict[str, list[tuple[str, dict]]] = {}
    for candidate_id, candidate in catalogue["items"].items():
        if candidate["status"] != "catalogue_supported":
            continue
        for app in candidate["applications"]:
            applications_by_file.setdefault(app["model_file"], []).append((candidate_id, app))
    changed_files, changed_records, skipped = [], [], []
    for relative, applications in sorted(applications_by_file.items()):
        path = ROOT / relative
        data = json.loads(path.read_text(encoding="utf-8"))
        detailed = isinstance(data.get("items"), dict)
        records = list(data.get("items", {}).values()) if detailed else data.get("generations", [])
        if not records:
            continue
        dirty = False
        for record in records:
            years = record_years(record)
            if years is None:
                continue
            start, end = years
            covering = [(cid, app) for cid, app in applications if scope_matches(record, app["key_variant_scope"]) and app["year_from"] <= start and app_end(app) >= end]
            covering_ids = {cid for cid, _ in covering}
            if family_id not in covering_ids:
                continue
            rid = record.get("record_id") or record.get("id")
            if len(covering_ids) != 1:
                skipped.append({"record_id": rid, "reason": "conflicting_catalogue_families", "families": sorted(covering_ids)})
                continue
            info = record.setdefault("vehicle_information", {}) if detailed else record
            target_id = family["repository_transponder_id"]
            display = family["display_name"]
            old_type, old_id = info.get("transponder_type"), info.get("transponder_id")
            if concrete(old_id) and old_id != target_id:
                skipped.append({"record_id": rid, "reason": "existing_concrete_id", "existing": old_id, "candidate": target_id})
                continue
            if concrete(old_type) and display.lower() not in old_type.lower() and old_id != target_id:
                skipped.append({"record_id": rid, "reason": "existing_concrete_type", "existing": old_type, "candidate": display})
                continue
            evidence_apps = [app for cid, app in covering if cid == family_id]
            evidence = []
            for source_id in sorted({app["source_id"] for app in evidence_apps}):
                source = catalogue["sources"][source_id]
                source_apps = [app for app in evidence_apps if app["source_id"] == source_id]
                evidence.append({
                    "source_id": source_id, "publisher": source["publisher"], "title": source["title"],
                    "edition": source["edition"], "url": source["url"],
                    "catalogue_rows": sorted({app["catalogue_row"] for app in source_apps}),
                })
            verification = info.get("transponder_verification", {})
            if not isinstance(verification, dict):
                verification = {}
            if old_type == display and old_id == target_id and verification.get("canonical_transponder_family_id") == family_id:
                continue
            if not concrete(old_type):
                info["transponder_type"] = display
            if not concrete(old_id):
                info["transponder_id"] = target_id
            verification.update({
                "status": "partially_verified", "confidence": "medium", "last_checked": "2026-07-18",
                "canonical_transponder_family_id": family_id, "record_year_range": f"{start}-{end}", "evidence": evidence,
            })
            info["transponder_verification"] = verification
            dirty = True
            changed_records.append({"record_id": rid, "file": relative, "years": [start, end]})
        if dirty:
            changed_files.append(relative)
            if args.apply:
                path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"family": family_id, "apply": args.apply, "changed_files": changed_files, "changed_records": changed_records, "skipped": skipped}, indent=2))


if __name__ == "__main__":
    main()
