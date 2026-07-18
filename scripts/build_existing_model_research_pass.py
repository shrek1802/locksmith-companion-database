#!/usr/bin/env python3
"""Build a complete unresolved-field and workshop queue for existing UK models."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VEHICLES = ROOT / "database" / "vehicles"
REPORT = ROOT / "reports" / "existing_uk_model_research_pass.json"
WORKSHOP = ROOT / "reports" / "workshop_verification_queue.json"
UNRESOLVED = {"research_required", "research_in_progress", "verification_required", "to_be_verified", "conditional", "partially_verified"}
STATUS_KEYS = {"status", "overall_status", "verification_status", "verification_state", "tool_support"}


def walk(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, str(key))
            yield child_path, str(key), child
            yield from walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, (*path, str(index)))


def normalise(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def evidence_needed(filename: str, json_path: str) -> list[str]:
    text = f"{filename} {json_path}".lower()
    needs = []
    if "procedure" in text or "add_key" in text or "all_keys_lost" in text or "akl" in text:
        needs.append("Exact model/generation/operation result from OEM or current tool-vendor coverage")
    if "module" in text or "location" in text or "obd" in text:
        needs.append("UK RHD workshop evidence or clearly identified UK RHD vehicle photographs")
    if "wiring" in text or "bench" in text or "eeprom" in text or "mcu" in text or "processor" in text:
        needs.append("Exact module part number plus authoritative wiring/processor/adapter documentation")
    if "tool" in text or "adapter" in text:
        needs.append("Current tool application list and exact required hardware/licence")
    if "photo" in text:
        needs.append("Verified original UK RHD workshop image with vehicle/generation context")
    return needs or ["Traceable model/generation evidence sufficient to resolve the recorded status"]


def main() -> int:
    model_results: dict[str, dict] = {}
    queue: dict[str, dict] = {}
    manufacturers: Counter[str] = Counter()

    for manufacturer_dir in sorted(path for path in VEHICLES.iterdir() if path.is_dir()):
        manufacturer = manufacturer_dir.name
        for model_dir in sorted(path for path in manufacturer_dir.iterdir() if path.is_dir()):
            model_key = f"{manufacturer}/{model_dir.name}"
            manufacturers[manufacturer] += 1
            counts: Counter[str] = Counter()
            unresolved_items = 0
            files_scanned = 0
            for path in sorted(model_dir.glob("*.json")):
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                    continue
                files_scanned += 1
                for json_path, key, value in walk(data):
                    if key not in STATUS_KEYS or not isinstance(value, str):
                        continue
                    status = normalise(value)
                    counts[status] += 1
                    if status not in UNRESOLVED:
                        continue
                    unresolved_items += 1
                    queue_id = f"{manufacturer}_{model_dir.name}_{path.stem}_{unresolved_items}"
                    queue[queue_id] = {
                        "manufacturer": manufacturer,
                        "model": model_dir.name,
                        "file": path.relative_to(ROOT).as_posix(),
                        "json_path": "/".join(json_path),
                        "current_status": status,
                        "evidence_needed": evidence_needed(path.name, "/".join(json_path)),
                        "workshop_action": "Verify on an exact UK RHD vehicle only where location or physical access is involved.",
                    }
            model_results[model_key] = {
                "manufacturer": manufacturer,
                "model": model_dir.name,
                "files_scanned": files_scanned,
                "status_counts": dict(sorted(counts.items())),
                "unresolved_items": unresolved_items,
                "research_pass": "completed_with_queue" if unresolved_items else "completed_no_tracked_gaps",
            }

    report = {
        "schema_version": "1.0",
        "generated_at": "2026-07-18",
        "scope": "All currently stored UK/RHD manufacturer model directories",
        "counts": {"manufacturers": len(manufacturers), "models": len(model_results), "unresolved_items": len(queue)},
        "manufacturer_model_counts": dict(sorted(manufacturers.items())),
        "items": model_results,
    }
    workshop = {
        "schema_version": "1.0",
        "generated_at": "2026-07-18",
        "market": "UK",
        "drive_side": "RHD",
        "count": len(queue),
        "items": queue,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    WORKSHOP.write_text(json.dumps(workshop, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
