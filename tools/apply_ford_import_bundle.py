#!/usr/bin/env python3
"""Apply the generated Ford import bundle without deleting richer live data.

The bundle maps repository-relative models.json paths to generated payloads.
Existing populated scalar values win. Missing scalars, list entries, records and
sources are added from the generated payload. A report is written for review.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE = ROOT / "imports" / "ford_import_ready_v4.json"
REPORT = ROOT / "database" / "vehicles" / "ford" / "FORD_IMPORT_REPORT.json"

EMPTY_STRINGS = {"", "verification required", "unknown", "n/a", "not available"}


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in EMPTY_STRINGS
    if isinstance(value, (list, dict)):
        return len(value) == 0
    return False


def merge(existing: Any, generated: Any, path: str, conflicts: list[dict[str, Any]]) -> Any:
    if isinstance(existing, dict) and isinstance(generated, dict):
        out = copy.deepcopy(existing)
        for key, g_value in generated.items():
            child = f"{path}.{key}" if path else key
            if key not in out:
                out[key] = copy.deepcopy(g_value)
            else:
                out[key] = merge(out[key], g_value, child, conflicts)
        return out

    if isinstance(existing, list) and isinstance(generated, list):
        out = copy.deepcopy(existing)
        for value in generated:
            if value not in out:
                out.append(copy.deepcopy(value))
        return out

    if is_empty(existing) and not is_empty(generated):
        return copy.deepcopy(generated)

    if not is_empty(existing) and not is_empty(generated) and existing != generated:
        conflicts.append({"path": path, "kept": existing, "generated": generated})
    return copy.deepcopy(existing)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    report: dict[str, Any] = {
        "bundle": str(args.bundle.relative_to(ROOT)),
        "apply": args.apply,
        "files": [],
        "totals": {"new_files": 0, "updated_files": 0, "new_records": 0, "conflicts": 0},
    }

    for rel_path, generated in sorted(bundle["files"].items()):
        target = ROOT / rel_path
        conflicts: list[dict[str, Any]] = []
        new_records = 0

        if target.exists():
            existing = json.loads(target.read_text(encoding="utf-8"))
            before = set(existing.get("items", {}))
            merged = merge(existing, generated, "", conflicts)
            after = set(merged.get("items", {}))
            new_records = len(after - before)
            state = "updated" if merged != existing else "unchanged"
            if state == "updated":
                report["totals"]["updated_files"] += 1
        else:
            merged = generated
            state = "new"
            new_records = len(generated.get("items", {}))
            report["totals"]["new_files"] += 1

        if args.apply and state in {"new", "updated"}:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        report["totals"]["new_records"] += new_records
        report["totals"]["conflicts"] += len(conflicts)
        report["files"].append({
            "path": rel_path,
            "state": state,
            "new_records": new_records,
            "conflict_count": len(conflicts),
            "conflicts": conflicts,
        })

    # Bump the Ford manufacturer manifest whenever applying an import.
    manifest_path = ROOT / "database" / "vehicles" / "ford" / "manifest.json"
    if args.apply and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["version"] = int(manifest.get("version", 0)) + 1
        manifest["updated_at"] = "2026-07-15"
        manifest["status"] = "ford_master_import_applied"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["totals"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
