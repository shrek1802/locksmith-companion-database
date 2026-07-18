#!/usr/bin/env python3
"""Index unique notes already held by verified generation-specific records."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VEHICLES = ROOT / "database" / "vehicles"


def verified(status: object) -> bool:
    return isinstance(status, str) and "verified" in status and "not_verified" not in status


def collect(node: object, found: dict[str, set[str]]) -> None:
    if isinstance(node, dict):
        record_id = node.get("record_id")
        verification = node.get("verification", {})
        if isinstance(record_id, str) and isinstance(verification, dict) and verified(verification.get("status")):
            candidates: list[object] = []
            vehicle_information = node.get("vehicle_information")
            if isinstance(vehicle_information, dict):
                candidates.append(vehicle_information.get("notes"))
            notes = node.get("notes")
            if isinstance(notes, dict):
                candidates.append(notes.get("job_notes"))
            for value in candidates:
                if isinstance(value, str):
                    text = " ".join(value.split())
                    if len(text) >= 20:
                        found[text].add(record_id)
        for value in node.values():
            collect(value, found)
    elif isinstance(node, list):
        for value in node:
            collect(value, found)


def main() -> int:
    files_changed = 0
    notes_added = 0
    for model_path in sorted(VEHICLES.glob("*/*/models.json")):
        notes_path = model_path.with_name("notes.json")
        if not notes_path.exists():
            continue
        model_data = json.loads(model_path.read_text(encoding="utf-8"))
        found: dict[str, set[str]] = defaultdict(set)
        collect(model_data, found)
        if not found:
            continue
        notes_data = json.loads(notes_path.read_text(encoding="utf-8"))
        items = notes_data.get("items")
        if not isinstance(items, dict):
            continue
        existing_text = {
            " ".join(item.get("text", "").split())
            for item in items.values()
            if isinstance(item, dict) and isinstance(item.get("text"), str)
        }
        manufacturer_id = notes_data.get("manufacturer", {}).get("id", model_path.parents[1].name)
        model_id = notes_data.get("model", {}).get("id", model_path.parent.name)
        changed = False
        for text, record_ids in sorted(found.items()):
            if text in existing_text:
                continue
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10]
            item_id = f"{manufacturer_id}_{model_id}_job_note_{digest}"
            items[item_id] = {
                "id": item_id,
                "display_name": "Generation-specific locksmith note",
                "text": text,
                "status": "partially_verified",
                "source_record_ids": sorted(record_ids),
            }
            notes_added += 1
            changed = True
        if changed:
            verification = notes_data.setdefault("verification", {})
            if verification.get("status") in {None, "not_verified", "research_required"}:
                verification["status"] = "partially_verified"
            verification["notes"] = (
                "Duplicate wording is collapsed in this index. Each note remains traceable to the "
                "verified generation-specific records in models.json."
            )
            notes_path.write_text(
                json.dumps(notes_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            files_changed += 1
    print(f"note files updated: {files_changed}")
    print(f"unique notes added: {notes_added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
