#!/usr/bin/env python3
"""Index service functions already documented in generation-specific model records."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VEHICLES = ROOT / "database" / "vehicles"
FUNCTION_NAMES = {
    "add_key": "Add Key",
    "all_keys_lost": "All Keys Lost",
    "read_original_key": "Read Original Key",
    "dealer_key_generation": "Dealer Key Generation",
}


def collect_operations(node: object, found: dict[str, set[str]]) -> None:
    if isinstance(node, dict):
        record_id = node.get("record_id")
        operations = node.get("operations")
        if isinstance(record_id, str) and isinstance(operations, dict):
            for operation in FUNCTION_NAMES:
                if isinstance(operations.get(operation), dict):
                    found[operation].add(record_id)
        for value in node.values():
            collect_operations(value, found)
    elif isinstance(node, list):
        for value in node:
            collect_operations(value, found)


def main() -> int:
    changed = 0
    functions_added = 0
    for model_path in sorted(VEHICLES.glob("*/*/models.json")):
        service_path = model_path.with_name("service_functions.json")
        if not service_path.exists():
            continue
        model_data = json.loads(model_path.read_text(encoding="utf-8"))
        found: dict[str, set[str]] = defaultdict(set)
        collect_operations(model_data, found)
        if not found:
            continue

        service_data = json.loads(service_path.read_text(encoding="utf-8"))
        items = service_data.get("items")
        if not isinstance(items, dict):
            # Preserve established alternative service-function structures.
            continue
        file_changed = False
        manufacturer_id = service_data.get("manufacturer", {}).get("id", model_path.parents[1].name)
        model_id = service_data.get("model", {}).get("id", model_path.parent.name)
        for operation, record_ids in sorted(found.items()):
            item_id = f"{manufacturer_id}_{model_id}_{operation}"
            legacy_generated = items.get(operation)
            if (
                isinstance(legacy_generated, dict)
                and legacy_generated.get("notes", "").startswith("Function is indexed from existing")
            ):
                items.pop(operation)
                file_changed = True
            if item_id in items or any(
                isinstance(item, dict) and item.get("operation") == operation for item in items.values()
            ):
                continue
            items[item_id] = {
                "id": item_id,
                "display_name": FUNCTION_NAMES[operation],
                "operation": operation,
                "availability": "Generation and variant dependent; use the matching record in models.json",
                "status": "partially_verified",
                "source_record_ids": sorted(record_ids),
                "notes": "Function is indexed from existing generation-specific operations; exact tool and security-access requirements remain record-specific.",
            }
            file_changed = True
            functions_added += 1
        if file_changed:
            verification = service_data.setdefault("verification", {})
            if verification.get("status") in {None, "not_verified", "research_required"}:
                verification["status"] = "partially_verified"
            verification["notes"] = (
                "Functions listed here are supported by existing generation-specific model records. "
                "Consult models.json for exact variant, tool and online requirements."
            )
            service_path.write_text(
                json.dumps(service_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            changed += 1
    print(f"service files updated: {changed}")
    print(f"service functions added: {functions_added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
