#!/usr/bin/env python3
"""Locksmith Companion database validator v2.

Blocking errors:
- Invalid JSON, duplicate JSON keys or invalid UTF-8
- Invalid root/items/sources structures
- Missing locally referenced source IDs
- Manifest path points outside the repository
- A manufacturer folder exists but its referenced manifest is missing
- Empty or malformed item records

Non-blocking warnings:
- Missing recommended metadata
- Duplicate IDs in unrelated catalogue files
- Unknown strict references from vehicle records
- Duplicate part numbers in unrelated records

Expected/allowed:
- The same ID appearing once in `_shared` and once in a hardware catalogue
- Compatibility IDs inside hardware/shared catalogue files that are not yet indexed
- A future manufacturer manifest path when its manufacturer folder has not been created yet
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEXT_REPORT = ROOT / "database-validation-report.txt"
MARKDOWN_REPORT = ROOT / "database-validation-summary.md"

IGNORED_DIRS = {
    ".git", "node_modules", "APK", "build", "dist", "__pycache__"
}

# Only these references are strict when used by vehicle records.
STRICT_VEHICLE_REFERENCE_FIELDS = {
    "tool_ids",
    "required_tool_ids",
    "tool_accessory_ids",
    "bypass_cable_ids",
    "solder_free_adapter_ids",
    "active_interface_ids",
    "bench_connection_ids",
    "programmer_adapter_ids",
    "platform_ids",
}

KEY_PROFILE_FIELDS = (
    "blade_profile", "transponder_id", "technology_family", "chip_type",
    "chip_ic", "remote_configuration", "frequency",
)
CHIP_TYPE_VALUES = {
    "Glass Chip", "Carbon Chip", "Ceramic Chip", "Integrated Remote Chip",
    "Integrated Proximity Chip", "PCB Mounted Chip", "No Separate Transponder",
    "Research Required",
}
REMOTE_CONFIGURATION_VALUES = {
    "Separate", "Integrated", "Integrated Proximity", "No Remote", "Research Required",
}

errors: list[str] = []
warnings: list[str] = []
notes: list[str] = []

item_locations: dict[str, list[str]] = defaultdict(list)
source_locations: dict[str, list[str]] = defaultdict(list)
part_locations: dict[str, list[str]] = defaultdict(list)
strict_references: list[tuple[str, str, str]] = []

stats = Counter()
category_counts = Counter()
manufacturer_counts = Counter()


class DuplicateKeyError(ValueError):
    pass


def duplicate_key_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def error(location: str, message: str) -> None:
    errors.append(f"ERROR: {location}: {message}")


def warning(location: str, message: str) -> None:
    warnings.append(f"WARNING: {location}: {message}")


def note(location: str, message: str) -> None:
    notes.append(f"NOTE: {location}: {message}")


def is_vehicle_file(path: Path) -> bool:
    parts = path.relative_to(ROOT).parts
    if "manufacturers" not in parts:
        return False
    if "_shared" in parts or "hardware" in parts:
        return False
    return path.name != "manifest.json"


def is_shared_file(label: str) -> bool:
    return "/_shared/" in f"/{label}"


def is_hardware_file(label: str) -> bool:
    return "/hardware/" in f"/{label}"


def allowed_shared_hardware_duplicate(locations: list[str]) -> bool:
    unique = set(locations)
    has_shared = any(is_shared_file(location) for location in unique)
    has_hardware = any(is_hardware_file(location) for location in unique)
    return has_shared and has_hardware and all(
        is_shared_file(location) or is_hardware_file(location)
        for location in unique
    )


def vehicle_model_scope(location: str) -> str | None:
    parts = Path(location).parts
    if len(parts) >= 5 and parts[:2] == ("database", "vehicles"):
        return "/".join(parts[:4])
    return None


def allowed_same_vehicle_duplicate(locations: list[str]) -> bool:
    scopes = {vehicle_model_scope(location) for location in locations}
    return None not in scopes and len(scopes) == 1


def allowed_report_index_duplicate(locations: list[str]) -> bool:
    """Reports and staged reference catalogues intentionally mirror entity IDs."""
    has_report = any(location.startswith("reports/") for location in locations)
    non_reports = [location for location in locations if not location.startswith("reports/")]
    return has_report and all(location.startswith("database/reference/") for location in non_reports)


def allowed_staged_reference_duplicate(locations: list[str]) -> bool:
    return all(location.startswith("database/reference/") for location in locations)


def json_files() -> list[Path]:
    return sorted(
        path for path in ROOT.rglob("*.json")
        if not any(part in IGNORED_DIRS for part in path.parts)
    )


def load(path: Path) -> Any | None:
    try:
        return json.loads(
            path.read_text(encoding="utf-8-sig"),
            object_pairs_hook=duplicate_key_hook,
        )
    except UnicodeDecodeError as exc:
        error(rel(path), f"not valid UTF-8: {exc}")
    except DuplicateKeyError as exc:
        error(rel(path), str(exc))
    except json.JSONDecodeError as exc:
        error(
            rel(path),
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        )
    return None


def strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [entry for entry in value if isinstance(entry, str)]
    return []


def validate_sources(path: Path, data: dict[str, Any]) -> None:
    label = rel(path)
    sources = data.get("sources")
    if sources is None:
        return
    if not isinstance(sources, dict):
        error(label, "`sources` must be an object")
        return

    local_ids = set(sources)
    stats["sources"] += len(sources)

    for source_id, source in sources.items():
        source_locations[source_id].append(label)
        if not isinstance(source, dict):
            error(label, f"source {source_id!r} must be an object")
            continue
        url = source.get("url")
        if url is not None and not isinstance(url, str):
            error(label, f"source {source_id!r} has a non-string URL")

    def check(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "source_ids":
                    for source_id in strings(value):
                        if source_id not in local_ids:
                            error(
                                label,
                                f"source ID {source_id!r} is used but not defined in this file",
                            )
                check(value)
        elif isinstance(node, list):
            for value in node:
                check(value)

    check(data)


def validate_items(path: Path, data: dict[str, Any]) -> None:
    label = rel(path)
    items = data.get("items")
    if items is None:
        return
    if not isinstance(items, dict):
        error(label, "`items` must be an object")
        return

    stats["items"] += len(items)
    category = data.get("category")
    manufacturer = data.get("manufacturer")

    if isinstance(category, str):
        category_counts[category] += len(items)
    if isinstance(manufacturer, dict) and isinstance(manufacturer.get("name"), str):
        manufacturer_counts[manufacturer["name"]] += len(items)

    for item_id, item in items.items():
        if not isinstance(item_id, str) or not item_id.strip():
            error(label, "contains an empty or non-string item ID")
            continue
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", item_id):
            warning(
                label,
                f"item ID {item_id!r} should use lowercase letters, numbers, underscores, dots or hyphens",
            )
        if not isinstance(item, dict) or not item:
            error(label, f"item {item_id!r} must be a non-empty object")
            continue

        item_locations[item_id].append(label)

        display_name = item.get("display_name")
        if not isinstance(display_name, str) or not display_name.strip():
            warning(label, f"item {item_id!r} has no valid `display_name`")

        part_number = item.get("part_number")
        if isinstance(part_number, str) and part_number.strip():
            normalized = re.sub(r"\s+", "", part_number).upper()
            part_locations[normalized].append(f"{label}#{item_id}")


def validate_structured_key_profiles(path: Path, data: dict[str, Any]) -> None:
    if path.name != "models.json" or "database" not in path.parts or "vehicles" not in path.parts:
        return
    label = rel(path)
    records: list[tuple[str, Any]] = list(data.get("items", {}).items())
    records.extend((entry.get("id", f"generation_{index}"), entry) for index, entry in enumerate(data.get("generations", [])))
    for record_id, record in records:
        if not isinstance(record, dict):
            continue
        info = record.get("vehicle_information", record)
        if not isinstance(info, dict):
            continue
        for field in KEY_PROFILE_FIELDS:
            value = info.get(field)
            if not isinstance(value, str) or not value.strip():
                error(label, f"record {record_id!r} requires non-empty structured field {field!r}")
        if info.get("chip_type") not in CHIP_TYPE_VALUES:
            error(label, f"record {record_id!r} has invalid chip_type {info.get('chip_type')!r}")
        if info.get("remote_configuration") not in REMOTE_CONFIGURATION_VALUES:
            error(label, f"record {record_id!r} has invalid remote_configuration {info.get('remote_configuration')!r}")
        evidence_map = info.get("key_profile_evidence")
        if not isinstance(evidence_map, dict):
            error(label, f"record {record_id!r} requires key_profile_evidence")
            continue
        for field in KEY_PROFILE_FIELDS:
            if not isinstance(evidence_map.get(field), list):
                error(label, f"record {record_id!r} evidence for {field!r} must be a list")


def validate_strict_vehicle_references(path: Path, data: dict[str, Any]) -> None:
    if not is_vehicle_file(path):
        return

    label = rel(path)

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in STRICT_VEHICLE_REFERENCE_FIELDS:
                    for reference in strings(value):
                        strict_references.append((label, key, reference))
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(data)


def resolve_manifest_target(manifest_path: Path, raw: str) -> Path | None:
    if not raw or raw.startswith(("http://", "https://")):
        return None
    clean = raw.split("#", 1)[0].split("?", 1)[0]
    if not clean.lower().endswith((".json", ".zip")):
        return None
    local_target = (manifest_path.parent / clean).resolve()
    root_target = (ROOT / clean).resolve()

    # Manifests historically use both paths relative to their own directory and
    # paths relative to the repository root. Prefer the local interpretation to
    # preserve existing behaviour, then accept an existing root-relative target.
    if local_target.exists() or not root_target.exists():
        return local_target
    return root_target


def validate_manifest(path: Path, data: dict[str, Any]) -> None:
    if path.name != "manifest.json":
        return

    label = rel(path)
    stats["manifests"] += 1

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "manifest" and isinstance(value, str):
                    target = resolve_manifest_target(path, value)
                    if target is not None:
                        try:
                            target.relative_to(ROOT)
                        except ValueError:
                            error(label, f"manifest path escapes repository: {value!r}")
                        else:
                            if not target.exists():
                                # If the manufacturer directory itself does not exist yet,
                                # this is a future placeholder, not a blocking error.
                                manufacturer_dir = target.parent
                                if manufacturer_dir.exists():
                                    error(label, f"manifest path is missing: {value!r}")
                                else:
                                    note(
                                        label,
                                        f"future manufacturer manifest not present yet: {value!r}",
                                    )
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(data)


def validate_file(path: Path) -> None:
    stats["json_files"] += 1
    data = load(path)
    if data is None:
        return

    label = rel(path)
    if not isinstance(data, dict):
        error(label, "root must be an object")
        return

    if path.name != "manifest.json" and "schema_version" not in data:
        warning(label, "recommended `schema_version` is missing")

    validate_items(path, data)
    validate_sources(path, data)
    validate_manifest(path, data)
    validate_strict_vehicle_references(path, data)
    validate_structured_key_profiles(path, data)


def validate_duplicates() -> None:
    for item_id, locations in sorted(item_locations.items()):
        unique = sorted(set(locations))
        if len(unique) < 2:
            continue
        if (
            allowed_shared_hardware_duplicate(unique)
            or allowed_same_vehicle_duplicate(unique)
            or allowed_report_index_duplicate(unique)
            or allowed_staged_reference_duplicate(unique)
        ):
            note(
                "GLOBAL",
                f"ID {item_id!r} is intentionally indexed in related catalogues",
            )
        else:
            warning(
                "GLOBAL",
                f"item ID {item_id!r} appears in unrelated files: {', '.join(unique)}",
            )

    for part_number, locations in sorted(part_locations.items()):
        unique = sorted(set(locations))
        if len(unique) > 1:
            warning(
                "GLOBAL",
                f"part number {part_number!r} appears more than once: {', '.join(unique)}",
            )


def validate_vehicle_references() -> None:
    known = set(item_locations)
    for label, field, reference in strict_references:
        if reference not in known:
            warning(label, f"{field} references unknown ID {reference!r}")


def make_reports() -> None:
    status = "FAIL" if errors else ("PASS WITH WARNINGS" if warnings else "PASS")

    text = [
        "Locksmith Companion Database Validation v2",
        "=" * 46,
        f"Status: {status}",
        f"JSON files checked: {stats['json_files']}",
        f"Manifests checked: {stats['manifests']}",
        f"Items indexed: {stats['items']}",
        f"Sources indexed: {stats['sources']}",
        f"Errors: {len(errors)}",
        f"Warnings: {len(warnings)}",
        f"Notes: {len(notes)}",
        "",
    ]

    for heading, entries in (
        ("ERRORS", errors),
        ("WARNINGS", warnings),
        ("NOTES", notes),
    ):
        if entries:
            text.extend([heading, "-" * 46, *entries, ""])

    if errors:
        text.append("FAIL: Blocking database errors were found.")
    elif warnings:
        text.append("PASS WITH WARNINGS: The database is structurally valid.")
    else:
        text.append("PASS: The database is valid and clean.")

    TEXT_REPORT.write_text("\n".join(text) + "\n", encoding="utf-8")
    print("\n".join(text))

    md = [
        "# Locksmith Companion Database Health",
        "",
        f"## {status}",
        "",
        "| Check | Result |",
        "|---|---:|",
        f"| JSON files | {stats['json_files']} |",
        f"| Manifests | {stats['manifests']} |",
        f"| Indexed items | {stats['items']} |",
        f"| Source records | {stats['sources']} |",
        f"| Blocking errors | {len(errors)} |",
        f"| Warnings | {len(warnings)} |",
        f"| Informational notes | {len(notes)} |",
        "",
    ]

    if manufacturer_counts:
        md += ["## Items by hardware manufacturer", "", "| Manufacturer | Items |", "|---|---:|"]
        for name, count in manufacturer_counts.most_common():
            md.append(f"| {name} | {count} |")
        md.append("")

    if category_counts:
        md += ["## Items by category", "", "| Category | Items |", "|---|---:|"]
        for name, count in category_counts.most_common():
            md.append(f"| {name} | {count} |")
        md.append("")

    if errors:
        md += ["## Blocking errors", ""]
        md += [f"- `{entry}`" for entry in errors]
        md.append("")

    if warnings:
        md += ["## Warnings", ""]
        md += [f"- `{entry}`" for entry in warnings]
        md.append("")

    if notes:
        md += [
            "## Expected or informational items",
            "",
            f"{len(notes)} expected/indexing notes were recorded in the text report.",
            "",
        ]

    MARKDOWN_REPORT.write_text("\n".join(md) + "\n", encoding="utf-8")

    # Display the health table directly on the GitHub Actions run page.
    summary_file = Path(str(Path.cwd() / ".github-step-summary"))
    github_summary = Path(str(__import__("os").environ.get("GITHUB_STEP_SUMMARY", "")))
    if str(github_summary):
        try:
            github_summary.write_text(MARKDOWN_REPORT.read_text(encoding="utf-8"), encoding="utf-8")
        except OSError:
            pass


def main() -> int:
    files = json_files()
    if not files:
        error("REPOSITORY", "no JSON files found")
    else:
        for path in files:
            validate_file(path)

    validate_duplicates()
    validate_vehicle_references()
    make_reports()
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
