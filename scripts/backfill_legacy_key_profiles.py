#!/usr/bin/env python3
"""Recover structured key-profile fields from legacy values already in vehicle records.

This script never performs web research and never infers chip IC or chip construction
from a transponder ID. It only copies explicit values already present in the same record.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
VEHICLES = ROOT / "database" / "vehicles"

FIELDS = (
    "blade_profile",
    "transponder_id",
    "technology_family",
    "chip_type",
    "chip_ic",
    "remote_configuration",
    "frequency",
)

PLACEHOLDERS = {
    "",
    "unknown",
    "research required",
    "research_required",
    "verification required",
    "awaiting verification",
    "not verified",
    "not yet verified",
    "to be verified",
}

CHIP_TYPES = {
    "glass chip": "Glass Chip",
    "carbon chip": "Carbon Chip",
    "ceramic chip": "Ceramic Chip",
    "integrated remote chip": "Integrated Remote Chip",
    "integrated proximity chip": "Integrated Proximity Chip",
    "pcb mounted chip": "PCB Mounted Chip",
    "no separate transponder": "No Separate Transponder",
}

SOURCE_FIELDS = {
    "blade_profile": (
        "blade", "blade_type", "key_blade", "blade_code", "key_profile",
        "emergency_blade", "blade_profile",
    ),
    "transponder_id": (
        "transponder", "transponder_type", "chip_id", "immo_chip",
        "transponder_id",
    ),
    "technology_family": (
        "transponder_family", "technology", "technology_family", "chip_family",
    ),
    "chip_ic": (
        "chip_or_ic", "chip_ic", "ic", "transponder_ic", "pcf_reference",
    ),
    "frequency": (
        "frequency", "frequency_mhz", "remote_frequency", "rf_frequency",
    ),
}


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return " / ".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def is_placeholder(value: Any) -> bool:
    return text(value).lower().replace("-", " ") in PLACEHOLDERS


def first_meaningful(sources: Iterable[dict[str, Any]], names: Iterable[str]) -> tuple[str, str] | None:
    for source in sources:
        for name in names:
            value = source.get(name)
            if not is_placeholder(value):
                return text(value), name
    return None


def normalise_frequency(value: str) -> str:
    raw = value.strip()
    match = re.fullmatch(r"(\d{3}(?:\.\d+)?)\s*(?:mhz)?", raw, flags=re.I)
    if match:
        number = match.group(1).rstrip("0").rstrip(".")
        return f"{number} MHz"
    return raw if "mhz" in raw.lower() else raw


def explicit_chip_type(sources: Iterable[dict[str, Any]]) -> tuple[str, str] | None:
    candidate_names = ("chip_type", "chip_construction", "construction", "transponder_construction")
    found = first_meaningful(sources, candidate_names)
    if not found:
        return None
    raw, source_name = found
    normalised = CHIP_TYPES.get(raw.lower().replace("_", " ").strip())
    return (normalised, source_name) if normalised else None


def normalise_remote(raw: str) -> str | None:
    value = raw.lower().replace("_", " ").replace("-", " ").strip()
    if not value:
        return None
    if any(token in value for token in ("proximity", "smart key", "keyless", "hands free")):
        return "Integrated Proximity"
    if any(token in value for token in ("no remote", "non remote", "plain key", "transponder key")):
        return "No Remote"
    if any(token in value for token in ("separate remote", "remote separate")):
        return "Separate"
    if any(token in value for token in ("integrated remote", "remote key", "flip remote", "flip key")):
        return "Integrated"
    return None


def explicit_remote(sources: Iterable[dict[str, Any]]) -> tuple[str, str] | None:
    names = (
        "remote_configuration", "remote_type", "key_type", "key_style",
        "proximity", "smart_key", "key_variants",
    )
    for source in sources:
        for name in names:
            value = source.get(name)
            if is_placeholder(value):
                continue
            normalised = normalise_remote(text(value))
            if normalised:
                return normalised, name
    return None


def evidence_map(info: dict[str, Any]) -> dict[str, list[Any]]:
    current = info.get("key_profile_evidence")
    if not isinstance(current, dict):
        current = {}
    for field in FIELDS:
        if not isinstance(current.get(field), list):
            current[field] = []
    info["key_profile_evidence"] = current
    return current


def add_evidence(evidence: dict[str, list[Any]], field: str, source_field: str) -> None:
    marker = {
        "source": "legacy_record_migration",
        "source_field": source_field,
        "status": "legacy_supported",
    }
    if marker not in evidence[field]:
        evidence[field].append(marker)


def process_record(record: dict[str, Any], counts: Counter[str]) -> bool:
    info = record.get("vehicle_information")
    if not isinstance(info, dict):
        info = record

    sources = [info, record]
    for section_name in ("key_information", "key_profile", "remote", "transponder"):
        section = record.get(section_name)
        if isinstance(section, dict):
            sources.append(section)

    evidence = evidence_map(info)
    changed = False

    for target in ("blade_profile", "transponder_id", "technology_family", "chip_ic", "frequency"):
        if not is_placeholder(info.get(target)):
            continue
        found = first_meaningful(sources, SOURCE_FIELDS[target])
        if not found:
            continue
        value, source_name = found
        if target == "frequency":
            value = normalise_frequency(value)
        info[target] = value
        add_evidence(evidence, target, source_name)
        counts[target] += 1
        changed = True

    if is_placeholder(info.get("chip_type")):
        found_chip = explicit_chip_type(sources)
        if found_chip:
            value, source_name = found_chip
            info["chip_type"] = value
            add_evidence(evidence, "chip_type", source_name)
            counts["chip_type"] += 1
            changed = True

    if is_placeholder(info.get("remote_configuration")):
        found_remote = explicit_remote(sources)
        if found_remote:
            value, source_name = found_remote
            info["remote_configuration"] = value
            add_evidence(evidence, "remote_configuration", source_name)
            counts["remote_configuration"] += 1
            changed = True

    if changed:
        info["structured_profile_source"] = "legacy_record_migration"
        if record is not info:
            record["vehicle_information"] = info
    return changed


def iter_records(data: dict[str, Any]) -> Iterable[dict[str, Any]]:
    items = data.get("items")
    if isinstance(items, dict):
        for record in items.values():
            if isinstance(record, dict):
                yield record
    generations = data.get("generations")
    if isinstance(generations, list):
        for record in generations:
            if isinstance(record, dict):
                yield record


def main() -> int:
    counts: Counter[str] = Counter()
    scanned = changed_records = changed_files = 0
    examples: list[tuple[str, dict[str, Any], dict[str, Any]]] = []

    for path in sorted(VEHICLES.glob("*/*/models.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        file_changed = False
        for record in iter_records(data):
            scanned += 1
            before_info = record.get("vehicle_information", record)
            before = {field: before_info.get(field) for field in FIELDS}
            if process_record(record, counts):
                changed_records += 1
                file_changed = True
                after_info = record.get("vehicle_information", record)
                if len(examples) < 20:
                    examples.append((str(path.relative_to(ROOT)), before, {field: after_info.get(field) for field in FIELDS}))
        if file_changed:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            changed_files += 1

    print(f"Records scanned: {scanned}")
    print(f"Records changed: {changed_records}")
    print(f"Files changed: {changed_files}")
    for field in FIELDS:
        print(f"{field} recovered: {counts[field]}")
    print("\nRepresentative before/after examples:")
    for path, before, after in examples:
        print(f"\n{path}")
        print("  before:", json.dumps(before, ensure_ascii=False))
        print("  after: ", json.dumps(after, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
