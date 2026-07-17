#!/usr/bin/env python3
"""Strict Volkswagen platform-first completion audit.

This script never guesses or modifies vehicle data. It validates the dual-name
immobiliser registry and the UK master mapping matrix, then writes a report that
separates structural failures from research still required.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FAMILIES_PATH = ROOT / "database/platforms/volkswagen/immobiliser_families.json"
MATRIX_PATH = ROOT / "research/volkswagen_master_matrix.json"
REPORT_PATH = ROOT / "reports/volkswagen_true_completion_audit.json"

REQUIRED_FAMILY_FIELDS = {
    "locksmith_name",
    "aliases",
    "tool_menu_names",
    "architecture",
    "verification_state",
    "sources",
}
REQUIRED_RECORD_FIELDS = {
    "record_id",
    "model",
    "generation",
    "uk_year_from",
    "uk_year_to",
    "platform_id",
    "mapping_state",
    "evidence",
}
VALID_STATES = {"verified", "partially_verified", "research_required"}
VALID_MAPPING_STATES = {
    "verified",
    "inherited_verified",
    "research_required",
    "excluded_non_uk",
}
PLACEHOLDER_MARKERS = {
    "todo",
    "tbc",
    "unknown",
    "placeholder",
    "guess",
    "likely",
    "probably",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return data


def is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def contains_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.strip().lower()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def source_is_usable(source: Any) -> bool:
    return (
        isinstance(source, dict)
        and is_nonempty_text(source.get("publisher"))
        and is_nonempty_text(source.get("title"))
        and is_nonempty_text(source.get("url"))
        and isinstance(source.get("supports"), list)
        and bool(source.get("supports"))
    )


def evidence_is_usable(evidence: Any) -> bool:
    if not isinstance(evidence, list) or not evidence:
        return False
    return all(
        isinstance(item, dict)
        and is_nonempty_text(item.get("source"))
        and is_nonempty_text(item.get("supports"))
        for item in evidence
    )


def audit() -> tuple[dict[str, Any], bool]:
    structural_errors: list[dict[str, Any]] = []
    research_required: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    try:
        families_document = load_json(FAMILIES_PATH)
    except Exception as exc:  # noqa: BLE001 - report exact validation failure
        families_document = {}
        structural_errors.append({"scope": "families", "error": str(exc)})

    try:
        matrix_document = load_json(MATRIX_PATH)
    except Exception as exc:  # noqa: BLE001
        matrix_document = {}
        structural_errors.append({"scope": "matrix", "error": str(exc)})

    families = families_document.get("families", {})
    if not isinstance(families, dict):
        structural_errors.append({"scope": "families", "error": "families must be an object"})
        families = {}

    family_state_counts: Counter[str] = Counter()

    for family_id, family in sorted(families.items()):
        if not isinstance(family, dict):
            structural_errors.append({"family_id": family_id, "error": "family must be an object"})
            continue

        missing = sorted(REQUIRED_FAMILY_FIELDS - set(family))
        if missing:
            structural_errors.append({"family_id": family_id, "missing_fields": missing})

        state = family.get("verification_state")
        family_state_counts[str(state)] += 1
        if state not in VALID_STATES:
            structural_errors.append({"family_id": family_id, "error": "invalid verification_state"})

        official_name = family.get("official_name")
        official_status = family.get("official_name_status")
        if official_name is None and not is_nonempty_text(official_status):
            structural_errors.append(
                {"family_id": family_id, "error": "official_name is null without official_name_status"}
            )

        if not is_nonempty_text(family.get("locksmith_name")):
            structural_errors.append({"family_id": family_id, "error": "locksmith_name is empty"})

        tool_names = family.get("tool_menu_names")
        if not isinstance(tool_names, dict):
            structural_errors.append({"family_id": family_id, "error": "tool_menu_names must be an object"})

        sources = family.get("sources")
        if state == "verified" and (not isinstance(sources, list) or not sources):
            structural_errors.append({"family_id": family_id, "error": "verified family has no sources"})
        elif isinstance(sources, list):
            for index, source in enumerate(sources):
                if not source_is_usable(source):
                    structural_errors.append(
                        {"family_id": family_id, "source_index": index, "error": "invalid source"}
                    )

        if state != "verified":
            research_required.append(
                {
                    "scope": "family",
                    "family_id": family_id,
                    "reason": f"verification_state={state}",
                }
            )

    records = matrix_document.get("records", [])
    if not isinstance(records, list):
        structural_errors.append({"scope": "matrix", "error": "records must be an array"})
        records = []

    seen_record_ids: set[str] = set()
    mapping_counts: Counter[str] = Counter()
    platform_usage: defaultdict[str, int] = defaultdict(int)

    for index, record in enumerate(records):
        location = {"scope": "record", "index": index}
        if not isinstance(record, dict):
            structural_errors.append({**location, "error": "record must be an object"})
            continue

        record_id = record.get("record_id")
        if is_nonempty_text(record_id):
            location["record_id"] = record_id
            if record_id in seen_record_ids:
                structural_errors.append({**location, "error": "duplicate record_id"})
            seen_record_ids.add(record_id)

        missing = sorted(REQUIRED_RECORD_FIELDS - set(record))
        if missing:
            structural_errors.append({**location, "missing_fields": missing})

        state = record.get("mapping_state")
        mapping_counts[str(state)] += 1
        if state not in VALID_MAPPING_STATES:
            structural_errors.append({**location, "error": "invalid mapping_state"})

        platform_id = record.get("platform_id")
        if not is_nonempty_text(platform_id) or platform_id not in families:
            structural_errors.append({**location, "error": "platform_id is missing or unknown"})
        else:
            platform_usage[platform_id] += 1

        year_from = record.get("uk_year_from")
        year_to = record.get("uk_year_to")
        if not isinstance(year_from, int) or not isinstance(year_to, int) or year_from > year_to:
            structural_errors.append({**location, "error": "invalid UK year range"})

        for field_name, value in record.items():
            if contains_placeholder(value):
                structural_errors.append(
                    {**location, "field": field_name, "error": "placeholder/guess marker found"}
                )

        evidence = record.get("evidence")
        if state in {"verified", "inherited_verified"} and not evidence_is_usable(evidence):
            structural_errors.append({**location, "error": "verified mapping has insufficient evidence"})

        if state == "inherited_verified" and platform_id in families:
            if families[platform_id].get("verification_state") != "verified":
                structural_errors.append(
                    {**location, "error": "inherits from a platform that is not verified"}
                )

        if state == "research_required":
            research_required.append(
                {**location, "platform_id": platform_id, "reason": "vehicle mapping requires research"}
            )

        if state == "excluded_non_uk" and record.get("market") == "UK":
            warnings.append({**location, "warning": "excluded_non_uk record declares UK market"})

    complete_records = mapping_counts["verified"] + mapping_counts["inherited_verified"]
    publishable = (
        not structural_errors
        and bool(records)
        and complete_records == len(records)
        and not research_required
    )

    report = {
        "schema_version": "1.0",
        "manufacturer": "Volkswagen",
        "market": "UK",
        "drive_side": "RHD",
        "counts": {
            "families": len(families),
            "family_states": dict(sorted(family_state_counts.items())),
            "records": len(records),
            "mapping_states": dict(sorted(mapping_counts.items())),
            "complete_records": complete_records,
            "structural_errors": len(structural_errors),
            "research_required": len(research_required),
            "warnings": len(warnings),
        },
        "platform_usage": dict(sorted(platform_usage.items())),
        "publishable": publishable,
        "structural_errors": structural_errors,
        "research_required": research_required,
        "warnings": warnings,
    }
    return report, not structural_errors


def main() -> int:
    report, structurally_valid = audit()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report["counts"], indent=2))
    print(f"publishable: {report['publishable']}")
    print(f"report: {REPORT_PATH.relative_to(ROOT)}")

    # Research-required is expected during construction. CI fails only for malformed,
    # conflicting or unsupported data; publishing remains blocked by publishable=false.
    return 0 if structurally_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
