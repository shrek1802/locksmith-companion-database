#!/usr/bin/env python3
"""Conservatively share Ford key hardware across genuinely equivalent records.

Only copies values when records already agree on a strong key signature:
transponder, blade, frequency, smart-key state and key type. This avoids
assigning an OEM number merely because two vehicles are close in year.
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"
TODAY = date.today().isoformat()
FIELDS = ("oem_part_numbers", "battery_type", "button_count", "emergency_blade", "aftermarket_references")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def useful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        text = value.strip().lower()
        return bool(text) and text not in {"unknown", "not verified", "verification required", "n/a"}
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def norm(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).lower().replace("—", "-").split())


def signature(info: dict[str, Any]) -> tuple[str, ...] | None:
    transponder = norm(info.get("transponder_id") or info.get("transponder_type"))
    blade = norm(info.get("blade_id") or info.get("blade_profile"))
    frequency = norm(info.get("frequency_id") or info.get("frequency_mhz"))
    key_type = norm(info.get("key_type"))
    smart = str(bool(info.get("smart_key")))
    if not transponder or not blade or not frequency or not key_type:
        return None
    return transponder, blade, frequency, key_type, smart


def merge_lists(values: list[Any]) -> list[Any]:
    result = []
    seen = set()
    for value in values:
        if not isinstance(value, list):
            continue
        for item in value:
            marker = json.dumps(item, sort_keys=True, ensure_ascii=False)
            if marker not in seen:
                seen.add(marker)
                result.append(item)
    return result


def consensus(values: list[Any]) -> Any:
    good = [v for v in values if useful(v)]
    if not good:
        return None
    if all(isinstance(v, list) for v in good):
        merged = merge_lists(good)
        return merged or None
    markers: dict[str, tuple[int, Any]] = {}
    for value in good:
        marker = json.dumps(value, sort_keys=True, ensure_ascii=False)
        count, _ = markers.get(marker, (0, value))
        markers[marker] = (count + 1, value)
    best = sorted(markers.values(), key=lambda item: item[0], reverse=True)
    if len(best) == 1 or best[0][0] > best[1][0]:
        return best[0][1]
    return None


def main() -> int:
    payloads: dict[Path, dict[str, Any]] = {}
    records: list[tuple[Path, str, dict[str, Any]]] = []
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)

    for path in sorted(FORD_ROOT.glob("*/models.json")):
        payload = load(path)
        payloads[path] = payload
        for record_id, record in payload.get("items", {}).items():
            if not isinstance(record, dict):
                continue
            records.append((path, record_id, record))
            info = record.get("vehicle_information", {})
            sig = signature(info)
            if sig:
                groups[sig].append(record)

    updates = defaultdict(int)
    touched_records = set()
    for path, record_id, record in records:
        info = record.setdefault("vehicle_information", {})
        sig = signature(info)
        if not sig or len(groups[sig]) < 2:
            continue
        peers = groups[sig]
        for field in FIELDS:
            if useful(info.get(field)):
                continue
            value = consensus([peer.get("vehicle_information", {}).get(field) for peer in peers])
            if useful(value):
                info[field] = value
                updates[field] += 1
                touched_records.add((str(path), record_id))
        if (str(path), record_id) in touched_records:
            verification = record.setdefault("verification", {})
            verification.setdefault("sources", []).append("equivalent_key_signature_consensus")
            verification["last_checked"] = TODAY
            verification["hardware_consensus_applied"] = True

    for path, payload in payloads.items():
        payload["updated_at"] = TODAY
        save(path, payload)

    queue = []
    for path, record_id, record in records:
        info = record.get("vehicle_information", {})
        missing = [field for field in ("oem_part_numbers", "button_count", "battery_type", "frequency_mhz", "blade_profile", "transponder_type") if not useful(info.get(field))]
        if missing:
            vehicle = record.get("vehicle", {})
            queue.append({
                "model_folder": path.parent.name,
                "record_id": record_id,
                "vehicle": {
                    "model": vehicle.get("model"),
                    "variant": vehicle.get("variant"),
                    "generation": vehicle.get("generation"),
                    "year_from": vehicle.get("year_from"),
                    "year_to": vehicle.get("year_to"),
                },
                "known_signature": {
                    "key_type": info.get("key_type"),
                    "transponder": info.get("transponder_type"),
                    "blade": info.get("blade_profile"),
                    "frequency": info.get("frequency_mhz"),
                    "smart_key": info.get("smart_key"),
                },
                "missing_fields": missing,
            })

    save(ROOT / "reports" / "ford_targeted_hardware_queue.json", {
        "generated_at": TODAY,
        "records": len(queue),
        "updates_applied": dict(updates),
        "touched_records": len(touched_records),
        "queue": queue,
    })
    print(json.dumps({"updates": dict(updates), "touched_records": len(touched_records), "remaining_queue": len(queue)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
