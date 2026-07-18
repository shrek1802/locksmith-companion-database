#!/usr/bin/env python3
"""Namespace vehicle item IDs that collide across different model folders."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VEHICLES = ROOT / "database" / "vehicles"


def main() -> int:
    occurrences: dict[str, list[Path]] = defaultdict(list)
    documents: dict[Path, dict] = {}
    for path in sorted(VEHICLES.glob("*/*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        documents[path] = data
        items = data.get("items") if isinstance(data, dict) else None
        if isinstance(items, dict):
            for item_id in items:
                occurrences[item_id].append(path)

    cross_model = {
        item_id
        for item_id, paths in occurrences.items()
        if len({path.parent for path in paths}) > 1
    }
    files_changed = 0
    ids_changed = 0
    for path, data in documents.items():
        items = data.get("items") if isinstance(data, dict) else None
        if not isinstance(items, dict) or not cross_model.intersection(items):
            continue
        manufacturer_id = path.parents[1].name
        model_id = path.parent.name
        updated: dict[str, object] = {}
        changed = False
        for item_id, item in items.items():
            new_id = f"{manufacturer_id}_{model_id}_{item_id}" if item_id in cross_model else item_id
            if new_id in updated:
                raise ValueError(f"item ID collision in {path}: {new_id}")
            if new_id != item_id and isinstance(item, dict):
                item.setdefault("legacy_item_id", item_id)
                if item.get("id") == item_id:
                    item["id"] = new_id
                changed = True
                ids_changed += 1
            updated[new_id] = item
        if changed:
            data["items"] = updated
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            files_changed += 1
    print(f"files updated: {files_changed}")
    print(f"item IDs namespaced: {ids_changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
