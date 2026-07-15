#!/usr/bin/env python3
"""Merge generated Ford models.json files into the live database safely.

The workbook-generated export is useful for OEM part numbers, stock details and
missing Locksmith Card fields, but it must not blindly replace richer live
records. This importer preserves existing verified fields and merges only data
that is missing or explicitly more useful.

Usage:
    python tools/merge_ford_generated_models.py \
        --generated /path/to/Ford_Import_Ready_v4/database/vehicles/ford \
        --live database/vehicles/ford \
        --report ford_merge_report.json

Run without --apply for a dry run. Add --apply to write merged files.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


PLACEHOLDER_TEXT = {
    "",
    "verification required",
    "not verified",
    "confirm",
    "unknown",
    "frequency_unknown",
    "transponder_unknown",
    "emergency_blade_unknown",
}


def is_placeholder(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        text = value.strip().lower()
        return not text or text in PLACEHOLDER_TEXT or "verification required" in text
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def merge_list(existing: list[Any], incoming: list[Any]) -> list[Any]:
    result = copy.deepcopy(existing)
    for item in incoming:
        if item not in result:
            result.append(copy.deepcopy(item))
    return result


def merge_dict(existing: dict[str, Any], incoming: dict[str, Any], path: str, changes: list[dict[str, Any]]) -> dict[str, Any]:
    result = copy.deepcopy(existing)
    for key, incoming_value in incoming.items():
        field_path = f"{path}.{key}" if path else key
        if key not in result or is_placeholder(result[key]):
            if not is_placeholder(incoming_value):
                result[key] = copy.deepcopy(incoming_value)
                changes.append({"field": field_path, "action": "filled", "value": incoming_value})
            continue

        existing_value = result[key]
        if isinstance(existing_value, dict) and isinstance(incoming_value, dict):
            result[key] = merge_dict(existing_value, incoming_value, field_path, changes)
        elif isinstance(existing_value, list) and isinstance(incoming_value, list):
            merged = merge_list(existing_value, incoming_value)
            if merged != existing_value:
                result[key] = merged
                changes.append({"field": field_path, "action": "extended", "value": merged})
        # Never overwrite a populated scalar automatically. Conflicting values
        # remain in the report for manual verification.
        elif existing_value != incoming_value and not is_placeholder(incoming_value):
            changes.append({
                "field": field_path,
                "action": "conflict_preserved_existing",
                "existing": existing_value,
                "incoming": incoming_value,
            })
    return result


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generated", required=True, type=Path)
    parser.add_argument("--live", required=True, type=Path)
    parser.add_argument("--report", type=Path, default=Path("ford_merge_report.json"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    report: dict[str, Any] = {
        "mode": "apply" if args.apply else "dry_run",
        "files": [],
        "summary": {"files_checked": 0, "files_changed": 0, "records_added": 0, "conflicts": 0},
    }

    for generated_file in sorted(args.generated.glob("*/models.json")):
        model_id = generated_file.parent.name
        live_file = args.live / model_id / "models.json"
        report["summary"]["files_checked"] += 1

        generated = load_json(generated_file)
        if not live_file.exists():
            entry = {"model": model_id, "action": "new_file", "records": len(generated.get("items", {}))}
            report["files"].append(entry)
            report["summary"]["files_changed"] += 1
            report["summary"]["records_added"] += len(generated.get("items", {}))
            if args.apply:
                live_file.parent.mkdir(parents=True, exist_ok=True)
                live_file.write_text(json.dumps(generated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            continue

        live = load_json(live_file)
        merged = copy.deepcopy(live)
        file_changes: list[dict[str, Any]] = []
        live_items = merged.setdefault("items", {})

        for record_key, incoming_record in generated.get("items", {}).items():
            if record_key not in live_items:
                live_items[record_key] = copy.deepcopy(incoming_record)
                file_changes.append({"record": record_key, "action": "record_added"})
                report["summary"]["records_added"] += 1
                continue

            record_changes: list[dict[str, Any]] = []
            live_items[record_key] = merge_dict(live_items[record_key], incoming_record, record_key, record_changes)
            if record_changes:
                file_changes.extend({"record": record_key, **change} for change in record_changes)

        merged["sources"] = merge_dict(merged.get("sources", {}), generated.get("sources", {}), "sources", file_changes)

        conflict_count = sum(1 for change in file_changes if change.get("action") == "conflict_preserved_existing")
        report["summary"]["conflicts"] += conflict_count
        if file_changes:
            report["summary"]["files_changed"] += 1
            if args.apply:
                live_file.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        report["files"].append({
            "model": model_id,
            "action": "merged" if file_changes else "unchanged",
            "changes": file_changes,
            "conflicts": conflict_count,
        })

    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
