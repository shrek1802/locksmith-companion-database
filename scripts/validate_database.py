#!/usr/bin/env python3
"""Validate the Locksmith Companion JSON database.

Hard failures:
- Invalid JSON or duplicate JSON object keys
- A JSON root that is not an object
- Invalid `items` or `sources` containers
- Missing local source IDs
- Broken manifest paths
- Duplicate item IDs inside one file
- Empty or invalid item records

Warnings:
- Duplicate IDs across separate catalogue files
- Duplicate part numbers
- Unknown cross-file references
- Missing recommended metadata
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "database-validation-report.txt"

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "APK",
    "build",
    "dist",
    "__pycache__",
}

REFERENCE_FIELDS = {
    "compatible_tool_ids",
    "compatible_programmer_ids",
    "compatible_interface_ids",
    "compatible_adapter_ids",
    "compatible_module_ids",
    "source_ids",
    "bypass_cable_ids",
    "solder_free_adapter_ids",
    "active_interface_ids",
    "bench_connection_ids",
    "tool_accessory_ids",
    "required_tool_ids",
}

MANIFEST_PATH_KEYS = {"manifest", "path", "file", "url"}

errors: list[str] = []
warnings: list[str] = []
info: list[str] = []

all_item_ids: dict[str, list[str]] = defaultdict(list)
all_source_ids: dict[str, list[str]] = defaultdict(list)
part_numbers: dict[str, list[str]] = defaultdict(list)
pending_references: list[tuple[str, str, str]] = []


class DuplicateKeyError(ValueError):
    pass


def duplicate_key_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise DuplicateKeyError(f"duplicate JSON key {key!r}")
        obj[key] = value
    return obj


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def add_error(path: Path | str, message: str) -> None:
    errors.append(f"ERROR: {path}: {message}")


def add_warning(path: Path | str, message: str) -> None:
    warnings.append(f"WARNING: {path}: {message}")


def iter_json_files() -> list[Path]:
    result: list[Path] = []
    for path in ROOT.rglob("*.json"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        result.append(path)
    return sorted(result)


def load_json(path: Path) -> Any | None:
    try:
        return json.loads(
            path.read_text(encoding="utf-8-sig"),
            object_pairs_hook=duplicate_key_hook,
        )
    except UnicodeDecodeError as exc:
        add_error(rel(path), f"file is not valid UTF-8: {exc}")
    except DuplicateKeyError as exc:
        add_error(rel(path), str(exc))
    except json.JSONDecodeError as exc:
        add_error(
            rel(path),
            f"invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        )
    return None


def collect_reference_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def walk_references(path_label: str, node: Any, parent_key: str = "") -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in REFERENCE_FIELDS or key.endswith("_ids"):
                for ref_value in collect_reference_values(value):
                    pending_references.append((path_label, key, ref_value))
            walk_references(path_label, value, key)
    elif isinstance(node, list):
        for value in node:
            walk_references(path_label, value, parent_key)


def validate_items(path: Path, data: dict[str, Any]) -> None:
    path_label = rel(path)
    items = data.get("items")
    if items is None:
        return
    if not isinstance(items, dict):
        add_error(path_label, "`items` must be a JSON object")
        return

    for item_id, item in items.items():
        if not isinstance(item_id, str) or not item_id.strip():
            add_error(path_label, "contains an empty or non-string item ID")
            continue
        if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", item_id):
            add_warning(
                path_label,
                f"item ID {item_id!r} should preferably use lowercase letters, numbers, underscores, dots or hyphens",
            )
        if not isinstance(item, dict):
            add_error(path_label, f"item {item_id!r} must be a JSON object")
            continue
        if not item:
            add_error(path_label, f"item {item_id!r} is empty")
            continue

        all_item_ids[item_id].append(path_label)

        display_name = item.get("display_name")
        if not isinstance(display_name, str) or not display_name.strip():
            add_warning(path_label, f"item {item_id!r} has no valid `display_name`")

        part_number = item.get("part_number")
        if isinstance(part_number, str) and part_number.strip():
            normalized = re.sub(r"\s+", "", part_number).upper()
            part_numbers[normalized].append(f"{path_label}#{item_id}")


def validate_sources(path: Path, data: dict[str, Any]) -> None:
    path_label = rel(path)
    sources = data.get("sources")
    if sources is None:
        return
    if not isinstance(sources, dict):
        add_error(path_label, "`sources` must be a JSON object")
        return

    local_source_ids = set(sources)
    for source_id, source in sources.items():
        all_source_ids[source_id].append(path_label)
        if not isinstance(source, dict):
            add_error(path_label, f"source {source_id!r} must be a JSON object")
            continue
        url = source.get("url")
        if url is not None and not isinstance(url, str):
            add_error(path_label, f"source {source_id!r} has a non-string `url`")

    def check_local_source_refs(node: Any) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "source_ids":
                    refs = collect_reference_values(value)
                    for source_id in refs:
                        if source_id not in local_source_ids:
                            add_error(
                                path_label,
                                f"source ID {source_id!r} is referenced but not defined in this file's `sources` object",
                            )
                check_local_source_refs(value)
        elif isinstance(node, list):
            for value in node:
                check_local_source_refs(value)

    check_local_source_refs(data)


def possible_manifest_path(base: Path, raw: str) -> Path | None:
    if not raw or raw.startswith(("http://", "https://")):
        return None
    clean = raw.split("#", 1)[0].split("?", 1)[0]
    if not clean.lower().endswith((".json", ".zip")):
        return None
    return (base / clean).resolve()


def validate_manifest_paths(path: Path, data: dict[str, Any]) -> None:
    path_label = rel(path)
    if path.name != "manifest.json":
        return

    def visit(node: Any, parent_key: str = "") -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key in MANIFEST_PATH_KEYS and isinstance(value, str):
                    target = possible_manifest_path(path.parent, value)
                    if target is not None:
                        try:
                            target.relative_to(ROOT)
                        except ValueError:
                            add_error(path_label, f"manifest path escapes the repository: {value!r}")
                        else:
                            if not target.exists():
                                add_error(
                                    path_label,
                                    f"manifest path does not exist: {value!r}",
                                )
                visit(value, key)
        elif isinstance(node, list):
            for value in node:
                visit(value, parent_key)

    visit(data)


def validate_file(path: Path) -> None:
    data = load_json(path)
    if data is None:
        return

    path_label = rel(path)
    if not isinstance(data, dict):
        add_error(path_label, "JSON root must be an object")
        return

    if "schema_version" not in data and path.name != "manifest.json":
        add_warning(path_label, "recommended top-level `schema_version` is missing")

    validate_items(path, data)
    validate_sources(path, data)
    validate_manifest_paths(path, data)
    walk_references(path_label, data)


def validate_global_duplicates() -> None:
    for item_id, locations in sorted(all_item_ids.items()):
        unique_locations = sorted(set(locations))
        if len(unique_locations) > 1:
            add_warning(
                "GLOBAL",
                f"item ID {item_id!r} appears in multiple files: {', '.join(unique_locations)}",
            )

    for part_number, locations in sorted(part_numbers.items()):
        unique_locations = sorted(set(locations))
        if len(unique_locations) > 1:
            add_warning(
                "GLOBAL",
                f"part number {part_number!r} appears more than once: {', '.join(unique_locations)}",
            )


def validate_cross_file_references() -> None:
    known_ids = set(all_item_ids) | set(all_source_ids)
    for path_label, field, reference in pending_references:
        if field == "source_ids":
            continue
        if reference not in known_ids:
            add_warning(
                path_label,
                f"{field} references unknown ID {reference!r}; this may be a display name or a missing catalogue record",
            )


def write_report(json_count: int) -> None:
    lines = [
        "Locksmith Companion Database Validation",
        "=" * 40,
        f"JSON files checked: {json_count}",
        f"Errors: {len(errors)}",
        f"Warnings: {len(warnings)}",
        "",
    ]

    if errors:
        lines.extend(["ERRORS", "-" * 40, *errors, ""])
    if warnings:
        lines.extend(["WARNINGS", "-" * 40, *warnings, ""])
    if not errors and not warnings:
        lines.append("PASS: No errors or warnings found.")
    elif not errors:
        lines.append("PASS WITH WARNINGS: No blocking errors found.")
    else:
        lines.append("FAIL: Blocking validation errors were found.")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


def main() -> int:
    json_files = iter_json_files()
    if not json_files:
        add_error("REPOSITORY", "no JSON files were found")
        write_report(0)
        return 1

    for path in json_files:
        validate_file(path)

    validate_global_duplicates()
    validate_cross_file_references()
    write_report(len(json_files))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
