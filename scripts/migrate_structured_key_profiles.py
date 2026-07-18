#!/usr/bin/env python3
"""Add the backwards-compatible structured locksmith key-profile fields."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-07-19"
UNKNOWN = "Research Required"
CHIP_TYPES = {
    "Glass Chip", "Carbon Chip", "Ceramic Chip", "Integrated Remote Chip",
    "Integrated Proximity Chip", "PCB Mounted Chip", "No Separate Transponder", UNKNOWN,
}
REMOTE_TYPES = {"Separate", "Integrated", "Integrated Proximity", "No Remote", UNKNOWN}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def iter_records(data: dict):
    for record in data.get("items", {}).values():
        yield record, record.get("vehicle_information", record)
    for record in data.get("generations", []):
        yield record, record.get("vehicle_information", record)


def evidence(verification: object) -> list[dict]:
    if not isinstance(verification, dict):
        return []
    return verification.get("evidence", []) or []


def source_ids(rows: list[dict]) -> set[str]:
    return {row.get("source_id") for row in rows if isinstance(row, dict) and row.get("source_id")}


def evidence_text(rows: list[dict]) -> str:
    return " ".join(json.dumps(row, ensure_ascii=False) for row in rows)


def normalise_frequency(info: dict) -> str:
    value = info.get("frequency")
    if value in (None, "", "research_required", UNKNOWN):
        value = info.get("frequency_mhz")
    if value in (None, "", "research_required", "unknown", "verification_required"):
        return UNKNOWN
    text = str(value).strip()
    if re.fullmatch(r"\d+(?:\.\d+)?", text):
        return f"{text} MHz"
    return text.replace("mhz", "MHz")


def migrate_record(record: dict, info: dict) -> Counter:
    stats = Counter(records_migrated=1)
    blade_evidence = evidence(info.get("blade_verification"))
    trans_evidence = evidence(info.get("transponder_verification"))
    frequency_evidence = evidence(info.get("frequency_verification"))
    trans_sources = source_ids(trans_evidence)
    trans_text = evidence_text(trans_evidence)
    descriptor = " ".join(str(value or "") for value in (
        info.get("key_type"), record.get("name"), record.get("vehicle", {}).get("variant"),
        record.get("vehicle", {}).get("ignition_type"),
    )).lower()

    for field in ("blade_profile", "transponder_id", "technology_family"):
        if info.get(field) in (None, "", "research_required", "unknown", "transponder_unknown"):
            info[field] = UNKNOWN

    chip_type = UNKNOWN
    remote = UNKNOWN
    if "keystation_texas_id60_2026" in trans_sources:
        chip_type, remote = "Glass Chip", "Separate"
    elif "keystation_texas_id63_2026" in trans_sources:
        chip_type, remote = "Carbon Chip", "Separate"
    elif ("PCF7941" in trans_text or "PCF7946" in trans_text) and any(word in descriptor for word in ("remote", "flip")):
        chip_type, remote = "Integrated Remote Chip", "Integrated"
    elif any(word in descriptor for word in ("proximity", "passive key", "smart key", "keyless")) and trans_evidence:
        chip_type, remote = "Integrated Proximity Chip", "Integrated Proximity"
    elif any(word in descriptor for word in ("non-remote", "no remote")) and trans_evidence:
        remote = "No Remote"

    chip_ic = info.get("chip_ic") or info.get("chip_or_ic")
    if not chip_ic or chip_ic in ("research_required", "unknown", UNKNOWN):
        chip_ic = UNKNOWN
    else:
        # A legacy IC value is retained only when the record already carries transponder evidence.
        if not trans_evidence or chip_ic not in trans_text:
            stats["unsupported_ic_assumptions_removed"] += 1
            chip_ic = UNKNOWN

    frequency = normalise_frequency(info)
    if frequency != UNKNOWN:
        stats["frequencies_preserved"] += 1

    info["chip_type"] = chip_type if chip_type in CHIP_TYPES else UNKNOWN
    info["chip_ic"] = chip_ic
    info["remote_configuration"] = remote if remote in REMOTE_TYPES else UNKNOWN
    info["frequency"] = frequency
    # Compatibility alias retained for consumers introduced by the preceding normalisation pass.
    info["chip_or_ic"] = None if chip_ic == UNKNOWN else chip_ic
    info["key_profile_evidence"] = {
        "blade_profile": blade_evidence,
        "transponder_id": trans_evidence,
        "technology_family": trans_evidence,
        "chip_type": trans_evidence if chip_type != UNKNOWN else [],
        "chip_ic": trans_evidence if chip_ic != UNKNOWN else [],
        "remote_configuration": trans_evidence if remote != UNKNOWN else [],
        "frequency": frequency_evidence or (blade_evidence if frequency != UNKNOWN else []),
    }
    stats[f"chip_type_{info['chip_type']}"] += 1
    if chip_ic != UNKNOWN:
        stats["exact_ic_values"] += 1
    return stats


def enrich_catalogue() -> None:
    path = ROOT / "database/reference/uk_transponder_catalogue.json"
    data = load(path)
    possible = {
        "philips_crypto2_id46": ["PCF7936", "PCF7941", "PCF7946"],
        "silca_id47": ["PCF7939FA"],
        "silca_id49_1c": ["PCF7938XA"],
        "silca_id49_1e": ["PCF7939MA"],
    }
    known_types = {
        "texas_crypto_id60": ["Glass Chip"],
        "texas_crypto_id63": ["Carbon Chip"],
    }
    for family_id, item in data["items"].items():
        item["known_possible_ics"] = possible.get(family_id, [])
        item["known_chip_types"] = known_types.get(family_id, [])
        item["confidence"] = item.get("family_verification", {}).get("confidence", item.get("confidence", "research_required"))
        if item["known_possible_ics"]:
            caution = "Possible ICs are family-level evidence only and must not be copied to a vehicle without exact application evidence."
            if caution not in item.get("notes", ""):
                item["notes"] = (item.get("notes", "") + " " + caution).strip()
    data["updated_at"] = DATE
    save(path, data)


def main() -> None:
    enrich_catalogue()
    totals = Counter()
    files = 0
    for path in sorted((ROOT / "database/vehicles").glob("*/*/models.json")):
        data = load(path)
        count = 0
        for record, info in iter_records(data):
            totals.update(migrate_record(record, info))
            count += 1
        if count:
            data["updated_at"] = DATE
            save(path, data)
            files += 1
    for chip_type in sorted(CHIP_TYPES):
        totals.setdefault(f"chip_type_{chip_type}", 0)
    totals.setdefault("exact_ic_values", 0)
    totals.setdefault("unsupported_ic_assumptions_removed", 0)
    totals.setdefault("frequencies_preserved", 0)
    report = {
        "schema_version": "2.2",
        "updated_at": DATE,
        "category": "structured_key_profile_migration_audit",
        "method": "Existing evidence only; no broad vehicle research and no classification from transponder ID alone.",
        "files_updated": files,
        "counts": dict(sorted(totals.items())),
        "app_source_status": "No editable app source is present; compiled APK files were not modified.",
    }
    save(ROOT / "reports/structured_key_profile_migration_audit.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
