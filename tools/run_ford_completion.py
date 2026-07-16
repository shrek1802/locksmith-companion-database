#!/usr/bin/env python3
"""Run the Ford rebuild and reliably publish its version/report.

This wrapper fixes the practical gaps in the Ford rebuild workflow:
1. the root manifest stores Ford version under manufacturers.ford;
2. all referenced tool IDs must exist in the shared tools catalogue;
3. legacy/generic Ford tool IDs are converted to the trimmed canonical catalogue.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import rebuild_all_ford_records

ROOT = Path(__file__).resolve().parents[1]
FORD_ROOT = ROOT / "database" / "vehicles" / "ford"
TOOLS_PATH = ROOT / "manufacturers" / "_shared" / "tools.json"
REPORT_PATH = ROOT / "reports" / "ford_full_rebuild_report.json"
TODAY = date.today().isoformat()

TOOL_ID_ALIASES = {
    "autel_im508s": "autel_im508s_xp400_pro",
    "autel_im608": "autel_im608_pro",
    "autel_km100": "autel_km100x",
    "xtool": "xtool_x100_pad2",
    "obdstar": "obdstar_g3",
    "obdstar_key_master_dp_plus": "obdstar_x300_dp_plus",
    "lonsdor": "lonsdor_k518_pro",
    "lonsdor_k518": "lonsdor_k518_pro",
}

REMOVED_NON_PRIMARY_TOOL_IDS = {
    "xhorse_vvdi_prog",
    "xtool_kc100",
    "xtool_kc501",
    "lonsdor_kh100_plus",
    "tmpro2",
    "orange5",
    "smok_uhds",
    "yanhua_acdp1",
    "yanhua_acdp2",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def canonicalise_ford_tool_ids() -> dict:
    changed_records = 0
    removed_ids: dict[str, int] = {}
    mapped_ids: dict[str, int] = {}

    for path in sorted(FORD_ROOT.glob("*/models.json")):
        data = load(path)
        file_changed = False
        for record in data.get("items", {}).values():
            if not isinstance(record, dict):
                continue
            info = record.setdefault("vehicle_information", {})
            raw_ids = info.get("tool_ids") if isinstance(info.get("tool_ids"), list) else []
            canonical = []
            for raw in raw_ids:
                tool_id = str(raw)
                if tool_id in REMOVED_NON_PRIMARY_TOOL_IDS:
                    removed_ids[tool_id] = removed_ids.get(tool_id, 0) + 1
                    continue
                mapped = TOOL_ID_ALIASES.get(tool_id, tool_id)
                if mapped != tool_id:
                    mapped_ids[f"{tool_id}->{mapped}"] = mapped_ids.get(f"{tool_id}->{mapped}", 0) + 1
                if mapped not in canonical:
                    canonical.append(mapped)
            if canonical != raw_ids:
                info["tool_ids"] = canonical
                changed_records += 1
                file_changed = True
        if file_changed:
            data["updated_at"] = TODAY
            data["tool_catalogue_normalised"] = True
            save(path, data)

    return {
        "changed_records": changed_records,
        "mapped_ids": mapped_ids,
        "removed_non_primary_ids": removed_ids,
    }


def bump_root_manifest() -> None:
    path = ROOT / "manifest.json"
    data = load(path)
    ford = data.setdefault("manufacturers", {}).setdefault("ford", {})
    ford["version"] = int(ford.get("version", 0)) + 1
    ford["status"] = "ford_full_record_rebuild"
    ford["updated_at"] = TODAY
    data["updated_at"] = TODAY
    save(path, data)


def validate_tool_ids() -> list[dict]:
    catalogue = load(TOOLS_PATH).get("tools", {})
    missing = []
    for path in sorted(FORD_ROOT.glob("*/models.json")):
        data = load(path)
        for record_id, record in data.get("items", {}).items():
            info = record.get("vehicle_information", {})
            for tool_id in info.get("tool_ids", []) or []:
                if tool_id not in catalogue:
                    missing.append({
                        "model": path.parent.name,
                        "record_id": record_id,
                        "tool_id": tool_id,
                    })
    return missing


def main() -> int:
    catalogue_changes = canonicalise_ford_tool_ids()
    rebuild_all_ford_records.main()
    bump_root_manifest()

    report = load(REPORT_PATH)
    missing_tool_ids = validate_tool_ids()
    report["tool_id_normalisation"] = catalogue_changes
    report["shared_tool_catalogue"] = {
        "path": str(TOOLS_PATH.relative_to(ROOT)),
        "missing_referenced_tool_ids": missing_tool_ids,
        "status": "pass" if not missing_tool_ids else "needs_mapping",
    }
    report["publication"] = {
        "root_manifest_ford_version_bumped": True,
        "published_at": TODAY,
    }
    save(REPORT_PATH, report)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if missing_tool_ids:
        raise SystemExit("Ford records reference tool IDs missing from manufacturers/_shared/tools.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
