#!/usr/bin/env python3
"""Backfill non-technical catalogue labels and recommended schema metadata."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCANNED_ROOTS = (ROOT / "database", ROOT / "reports")
EXCLUDED_PATHS = {
    ROOT / "reports" / "ford_true_completion_audit.json",
    ROOT / "reports" / "shared_verified_architecture_audit.json",
    ROOT / "reports" / "volkswagen_true_completion_audit.json",
}


def label(item_id: str, item: dict[str, object]) -> str:
    for key in ("name", "title", "summary", "text", "description"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            clean = " ".join(value.split())
            return clean if len(clean) <= 120 else clean[:117].rstrip() + "..."
    words = re.sub(r"[_\-.]+", " ", item_id).strip()
    return words[:1].upper() + words[1:] if words else "Unnamed catalogue item"


def main() -> int:
    changed_files = 0
    labels_added = 0
    schemas_added = 0
    item_ids_normalised = 0
    paths = sorted(
        path for root in SCANNED_ROOTS for path in root.rglob("*.json") if path not in EXCLUDED_PATHS
    )
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict):
            continue
        changed = False
        if "schema_version" not in data:
            data["schema_version"] = "2.1"
            schemas_added += 1
            changed = True
        items = data.get("items")
        if isinstance(items, dict):
            normalised_items: dict[str, object] = {}
            for item_id, item in items.items():
                normalised_id = str(item_id).replace("/", ".").casefold()
                if normalised_id != item_id and isinstance(item, dict):
                    item.setdefault("legacy_item_id", item_id)
                    item_ids_normalised += 1
                    changed = True
                if normalised_id in normalised_items:
                    raise ValueError(f"normalised item ID collision in {path}: {normalised_id}")
                normalised_items[normalised_id] = item
            if normalised_items.keys() != items.keys():
                data["items"] = items = normalised_items
            for item_id, item in items.items():
                if not isinstance(item, dict):
                    continue
                display_name = item.get("display_name")
                if not isinstance(display_name, str) or not display_name.strip():
                    item["display_name"] = label(str(item_id), item)
                    labels_added += 1
                    changed = True
        if changed:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            changed_files += 1
    print(f"files updated: {changed_files}")
    print(f"display names added: {labels_added}")
    print(f"schema versions added: {schemas_added}")
    print(f"item IDs normalised: {item_ids_normalised}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
