#!/usr/bin/env python3
"""Apply generated Ford import bundles without deleting richer live data."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IMPORT_DIR = ROOT / "imports"
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
            out[key] = copy.deepcopy(g_value) if key not in out else merge(out[key], g_value, child, conflicts)
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


def load_bundles(explicit: Path | None) -> tuple[list[str], dict[str, Any]]:
    paths = [explicit] if explicit else sorted(IMPORT_DIR.glob("ford_import_ready_v4_part*.json"))
    if not paths:
        raise FileNotFoundError("No Ford import bundle parts found")
    combined: dict[str, Any] = {}
    names: list[str] = []
    for path in paths:
        bundle = json.loads(path.read_text(encoding="utf-8"))
        names.append(str(path.relative_to(ROOT)))
        for rel_path, payload in bundle.get("files", {}).items():
            if rel_path in combined:
                raise ValueError(f"Duplicate generated path across bundle parts: {rel_path}")
            combined[rel_path] = payload
    return names, combined


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    bundle_names, files = load_bundles(args.bundle)
    report: dict[str, Any] = {
        "bundles": bundle_names,
        "apply": args.apply,
        "files": [],
        "totals": {"bundle_files": len(files), "new_files": 0, "updated_files": 0, "new_records": 0, "conflicts": 0},
    }

    for rel_path, generated in sorted(files.items()):
        target = ROOT / rel_path
        conflicts: list[dict[str, Any]] = []
        if target.exists():
            existing = json.loads(target.read_text(encoding="utf-8"))
            before = set(existing.get("items", {}))
            merged = merge(existing, generated, "", conflicts)
            new_records = len(set(merged.get("items", {})) - before)
            state = "updated" if merged != existing else "unchanged"
            if state == "updated": report["totals"]["updated_files"] += 1
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
        report["files"].append({"path": rel_path, "state": state, "new_records": new_records, "conflict_count": len(conflicts), "conflicts": conflicts})

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
