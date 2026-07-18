#!/usr/bin/env python3
"""Apply one canonical blade family to exact, fully covered vehicle records."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "database" / "reference" / "uk_blade_catalogue.json"
UNCERTAIN = re.compile(r"unknown|research|required|confirm|likely|var(?:y|ies|iant)|tbc|tbd|not recorded|exact physical", re.I)


def concrete(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and not UNCERTAIN.search(value)


def parse_years(value: Any) -> tuple[int, int] | None:
    if isinstance(value, str):
        years = [int(year) for year in re.findall(r"(?:19|20)\d{2}", value)]
        if not years:
            return None
        end = years[1] if len(years) > 1 else (2026 if re.search(r"present|current", value, re.I) else years[0])
        return years[0], end
    return None


def record_years(record: dict, detailed: bool) -> tuple[int, int] | None:
    if detailed:
        vehicle = record.get("vehicle", {})
        start, end = vehicle.get("year_from"), vehicle.get("year_to")
        if isinstance(start, int):
            return start, end if isinstance(end, int) else 2026
        return None
    return parse_years(record.get("years"))


def app_end(application: dict) -> int:
    if isinstance(application.get("year_to"), int):
        return application["year_to"]
    return 2025 if application["source_id"] == "silca_proximity_slot_remote_2025" else 2014


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--family", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    family_id = args.family.lower()
    if family_id not in catalogue["items"]:
        raise SystemExit(f"Unknown blade family: {args.family}")
    family_name = catalogue["items"][family_id]["display_name"]

    applications_by_file: dict[str, list[tuple[str, dict]]] = {}
    for candidate_id, family in catalogue["items"].items():
        for application in family["applications"]:
            applications_by_file.setdefault(application["model_file"], []).append((candidate_id, application))

    changed_files: list[str] = []
    changed_records: list[dict] = []
    skipped_conflicts: list[dict] = []

    for relative, applications in sorted(applications_by_file.items()):
        path = ROOT / relative
        data = json.loads(path.read_text(encoding="utf-8"))
        detailed = isinstance(data.get("items"), dict)
        records = list(data["items"].values()) if detailed else data.get("generations", [])
        file_changed = False

        for record in records:
            years = record_years(record, detailed)
            if years is None:
                continue
            start, end = years
            full_cover = [
                (candidate_id, application)
                for candidate_id, application in applications
                if application["year_from"] <= start and app_end(application) >= end
            ]
            covering_families = {candidate_id for candidate_id, _ in full_cover}
            if family_id not in covering_families:
                continue
            record_id = record.get("record_id") or record.get("id")
            if len(covering_families) != 1:
                skipped_conflicts.append({"record_id": record_id, "families": sorted(covering_families), "file": relative})
                continue

            target = record.setdefault("vehicle_information", {}) if detailed else record
            existing_profile = target.get("blade_profile")
            existing_id = target.get("blade_id")
            if concrete(existing_profile) and existing_profile.upper() != family_name:
                skipped_conflicts.append({"record_id": record_id, "existing": existing_profile, "candidate": family_name, "file": relative})
                continue
            if concrete(existing_id) and existing_id.lower() != family_id:
                skipped_conflicts.append({"record_id": record_id, "existing_id": existing_id, "candidate": family_id, "file": relative})
                continue
            if existing_profile == family_name and existing_id == family_id:
                continue

            evidence_apps = [application for candidate_id, application in full_cover if candidate_id == family_id]
            source_ids = sorted({application["source_id"] for application in evidence_apps})
            status = "verified" if len(source_ids) > 1 else "partially_verified"
            confidence = "high" if status == "verified" else "medium"
            evidence = []
            for source_id in source_ids:
                source = catalogue["sources"][source_id]
                rows = [app for app in evidence_apps if app["source_id"] == source_id]
                evidence.append({
                    "source_id": source_id,
                    "publisher": source["publisher"],
                    "title": source["title"],
                    "edition": source["edition"],
                    "url": source["url"],
                    "catalogue_rows": [row["catalogue_row"] for row in rows],
                })

            target["blade_profile"] = family_name
            target["blade_id"] = family_id
            verification = {
                "status": status,
                "confidence": confidence,
                "last_checked": "2026-07-18",
                "canonical_blade_family_id": family_id,
                "record_year_range": f"{start}-{end}",
                "evidence": evidence,
            }
            if detailed:
                target["blade_verification"] = verification
            else:
                record["blade_verification"] = verification
            file_changed = True
            changed_records.append({"record_id": record_id, "file": relative, "years": [start, end], "status": status})

        if file_changed:
            changed_files.append(relative)
            if args.apply:
                path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "family": family_name,
        "apply": args.apply,
        "changed_files": changed_files,
        "changed_records": changed_records,
        "skipped_conflicts": skipped_conflicts,
    }, indent=2))


if __name__ == "__main__":
    main()
