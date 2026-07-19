#!/usr/bin/env python3
"""Apply unambiguous UK blade/transponder catalogue mappings to vehicle records.

Dry-run by default. Use --apply to write changes.

The script never invents values and never overwrites concrete structured values.
It matches catalogue applications by manufacturer, model, year overlap and key
variant scope, records traceable evidence, and writes JSON/Markdown reports.
"""
from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
VEHICLES = ROOT / "database" / "vehicles"
REFERENCE = ROOT / "database" / "reference"
REPORTS = ROOT / "reports"

BLADE_CATALOGUE = REFERENCE / "uk_blade_catalogue.json"
TRANSPONDER_CATALOGUE = REFERENCE / "uk_transponder_catalogue.json"

PLACEHOLDERS = {
    "", "unknown", "research required", "research_required",
    "verification required", "awaiting verification", "not verified",
    "not yet verified", "to be verified", "n/a", "none", "null",
}


def norm(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return re.sub(r"_+", "_", text).strip("_")


def meaningful(value: Any) -> bool:
    return isinstance(value, (str, int, float)) and norm(value) not in PLACEHOLDERS


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def first(data: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = data.get(key)
        if meaningful(value):
            return value
    return None


def parse_years(record: dict[str, Any]) -> tuple[int | None, int | None]:
    candidates = [
        record.get("years"), record.get("year_range"), record.get("year"),
        record.get("production_years"), record.get("model_years"),
    ]
    for value in candidates:
        if isinstance(value, dict):
            start = value.get("from") or value.get("start") or value.get("year_from")
            end = value.get("to") or value.get("end") or value.get("year_to")
            return to_year(start), to_year(end)
        if isinstance(value, (int, float)):
            year = int(value)
            return year, year
        if isinstance(value, str):
            nums = [int(x) for x in re.findall(r"(?:19|20)\d{2}", value)]
            if nums:
                return min(nums), max(nums)
    start = to_year(record.get("year_from") or record.get("start_year"))
    end = to_year(record.get("year_to") or record.get("end_year"))
    return start, end


def to_year(value: Any) -> int | None:
    try:
        year = int(value)
        return year if 1900 <= year <= 2100 else None
    except (TypeError, ValueError):
        return None


def year_matches(record_years: tuple[int | None, int | None], app: dict[str, Any]) -> bool:
    r0, r1 = record_years
    a0 = to_year(app.get("year_from") or app.get("from") or app.get("start_year"))
    a1 = to_year(app.get("year_to") or app.get("to") or app.get("end_year"))
    if not any((r0, r1, a0, a1)):
        return True
    r0 = r0 or r1 or 1900
    r1 = r1 or r0 or 2100
    a0 = a0 or a1 or 1900
    a1 = a1 or a0 or 2100
    return max(r0, a0) <= min(r1, a1)


def record_scope(record: dict[str, Any]) -> set[str]:
    info = record.get("vehicle_information") if isinstance(record.get("vehicle_information"), dict) else record
    bits: list[str] = []
    for key in (
        "id", "name", "variant", "key_type", "key_style", "remote_type",
        "remote_configuration", "entry_type", "ignition_type", "key_variants",
    ):
        value = record.get(key)
        if value is None:
            value = info.get(key)
        if isinstance(value, list):
            bits.extend(str(x.get("type", x) if isinstance(x, dict) else x) for x in value)
        elif value is not None:
            bits.append(str(value))
    text = norm(" ".join(bits))
    scopes = set(filter(None, text.split("_")))
    if any(x in text for x in ("proximity", "smart_key", "keyless", "kessy")):
        scopes |= {"proximity", "smart", "keyless", "emergency", "insert"}
    if "slot" in text:
        scopes |= {"slot", "slot_key"}
    if any(x in text for x in ("flip", "remote_key", "integrated_remote")):
        scopes |= {"remote", "integrated", "flip"}
    if any(x in text for x in ("plain_key", "non_remote", "transponder_key", "keyed")):
        scopes |= {"keyed", "transponder", "standard"}
    return scopes


def scope_matches(record_scopes: set[str], app: dict[str, Any]) -> bool:
    raw = app.get("key_variant_scope") or app.get("variant_scope") or app.get("key_type")
    if not meaningful(raw):
        return True
    required = set(norm(raw).split("_")) - {"or", "and", "key"}
    if not required:
        return True
    return bool(required & record_scopes)


def iter_catalogue_entries(data: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    items = data.get("items")
    if isinstance(items, dict):
        yield from ((str(k), v) for k, v in items.items() if isinstance(v, dict))
    elif isinstance(items, list):
        for i, entry in enumerate(items):
            if isinstance(entry, dict):
                yield str(entry.get("id", i)), entry


def catalogue_applications(kind: str, data: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family_id, family in iter_catalogue_entries(data):
        applications = family.get("applications") or family.get("vehicle_applications") or []
        if not isinstance(applications, list):
            continue
        canonical = (
            family.get("canonical_id") or family.get("blade_profile") or
            family.get("profile") or family.get("display_name") or family_id
        )
        for application in applications:
            if not isinstance(application, dict):
                continue
            rows.append({
                "kind": kind,
                "family_id": family_id,
                "canonical": str(canonical),
                "family": family,
                "application": application,
            })
    return rows


def identity_matches(manufacturer: str, model: str, app: dict[str, Any]) -> bool:
    app_make = norm(app.get("manufacturer") or app.get("make") or app.get("brand"))
    app_model = norm(app.get("model") or app.get("vehicle_model"))
    if app_make and app_make != norm(manufacturer):
        return False
    if not app_model:
        return True
    model_n = norm(model)
    return app_model == model_n or app_model in model_n or model_n in app_model


def evidence_for(match: dict[str, Any]) -> dict[str, Any]:
    family = match["family"]
    app = match["application"]
    evidence = app.get("evidence") or app.get("evidence_source_ids") or family.get("evidence") or []
    if isinstance(evidence, str):
        evidence = [evidence]
    return {
        "source": f"canonical_{match['kind']}_catalogue",
        "catalogue_family_id": match["family_id"],
        "canonical_value": match["canonical"],
        "publisher": app.get("publisher") or family.get("publisher"),
        "title": app.get("title") or family.get("title") or family.get("display_name"),
        "rows": app.get("rows") or app.get("row") or app.get("page"),
        "url": app.get("url") or family.get("url"),
        "evidence": evidence,
        "confidence": app.get("confidence") or family.get("confidence") or "catalogue_supported",
    }


def candidate_matches(
    catalogue: list[dict[str, Any]], manufacturer: str, model: str,
    years: tuple[int | None, int | None], scopes: set[str],
) -> list[dict[str, Any]]:
    matches = []
    for item in catalogue:
        app = item["application"]
        if not identity_matches(manufacturer, model, app):
            continue
        if not year_matches(years, app):
            continue
        if not scope_matches(scopes, app):
            continue
        matches.append(item)
    unique: dict[tuple[str, str], dict[str, Any]] = {}
    for match in matches:
        unique[(match["family_id"], match["canonical"])] = match
    return list(unique.values())


def ensure_evidence(info: dict[str, Any]) -> dict[str, list[Any]]:
    evidence = info.get("key_profile_evidence")
    if not isinstance(evidence, dict):
        evidence = {}
        info["key_profile_evidence"] = evidence
    for field in (
        "blade_profile", "transponder_id", "technology_family", "chip_type",
        "chip_ic", "remote_configuration", "frequency",
    ):
        if not isinstance(evidence.get(field), list):
            evidence[field] = []
    return evidence


def apply_field(info: dict[str, Any], field: str, value: str, evidence: dict[str, Any], stats: Counter) -> bool:
    if meaningful(info.get(field)):
        return False
    info[field] = value
    emap = ensure_evidence(info)
    emap[field] = [evidence]
    info["structured_profile_source"] = "canonical_catalogue_mapping"
    info["structured_profile_status"] = "catalogue_supported"
    stats[field] += 1
    return True


def enrich_record(
    record: dict[str, Any], manufacturer: str, model: str,
    blades: list[dict[str, Any]], transponders: list[dict[str, Any]],
    stats: Counter, conflicts: list[dict[str, Any]], path: Path, record_id: str,
) -> bool:
    info = record.get("vehicle_information")
    if not isinstance(info, dict):
        info = record
    years = parse_years({**record, **info})
    scopes = record_scope(record)
    changed = False

    blade_matches = candidate_matches(blades, manufacturer, model, years, scopes)
    blade_values = sorted({m["canonical"] for m in blade_matches})
    if len(blade_values) == 1:
        match = next(m for m in blade_matches if m["canonical"] == blade_values[0])
        changed |= apply_field(info, "blade_profile", blade_values[0], evidence_for(match), stats)
        if not meaningful(info.get("blade_id")):
            info["blade_id"] = match["family_id"]
    elif len(blade_values) > 1:
        conflicts.append(conflict_row("blade", path, record_id, manufacturer, model, years, scopes, blade_matches))
        stats["blade_conflicts"] += 1

    trans_matches = candidate_matches(transponders, manufacturer, model, years, scopes)
    trans_values = sorted({m["canonical"] for m in trans_matches})
    if len(trans_values) == 1:
        match = next(m for m in trans_matches if m["canonical"] == trans_values[0])
        ev = evidence_for(match)
        changed |= apply_field(info, "transponder_id", trans_values[0], ev, stats)
        if not meaningful(info.get("transponder_type")):
            info["transponder_type"] = trans_values[0]
        family = match["family"]
        tech = family.get("technology_family")
        if meaningful(tech):
            changed |= apply_field(info, "technology_family", str(tech), ev, stats)
    elif len(trans_values) > 1:
        conflicts.append(conflict_row("transponder", path, record_id, manufacturer, model, years, scopes, trans_matches))
        stats["transponder_conflicts"] += 1

    return changed


def conflict_row(kind: str, path: Path, record_id: str, manufacturer: str, model: str,
                 years: tuple[int | None, int | None], scopes: set[str], matches: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "kind": kind,
        "path": str(path.relative_to(ROOT)),
        "record_id": record_id,
        "manufacturer": manufacturer,
        "model": model,
        "year_from": years[0],
        "year_to": years[1],
        "record_scopes": sorted(scopes),
        "matches": [
            {
                "family_id": m["family_id"],
                "canonical": m["canonical"],
                "application": m["application"],
            }
            for m in matches
        ],
        "recommended_action": "Split the record at the catalogue year/variant boundary or verify the exact application.",
    }


def records_from(data: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    items = data.get("items")
    if isinstance(items, dict):
        rows.extend((str(k), v) for k, v in items.items() if isinstance(v, dict))
    generations = data.get("generations")
    if isinstance(generations, list):
        rows.extend((str(v.get("id", f"generation_{i}")), v) for i, v in enumerate(generations) if isinstance(v, dict))
    return rows


def summary_markdown(summary: dict[str, Any], conflicts: list[dict[str, Any]]) -> str:
    lines = [
        "# Canonical Mapping Report", "",
        f"Generated: {summary['generated_at']}", "",
        "## Summary", "",
    ]
    for key, value in summary.items():
        if key != "generated_at":
            lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
    lines += ["", "## Conflicts", ""]
    if not conflicts:
        lines.append("No conflicts detected.")
    else:
        for row in conflicts:
            values = ", ".join(sorted({m['canonical'] for m in row['matches']}))
            lines.append(
                f"- `{row['path']}#{row['record_id']}` — {row['kind']} conflict: {values}"
            )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write updated models.json files")
    parser.add_argument("--report-dir", type=Path, default=REPORTS)
    args = parser.parse_args()

    blades = catalogue_applications("blade", load_json(BLADE_CATALOGUE))
    transponders = catalogue_applications("transponder", load_json(TRANSPONDER_CATALOGUE))
    stats: Counter = Counter()
    conflicts: list[dict[str, Any]] = []
    changed_files = 0

    for path in sorted(VEHICLES.glob("*/*/models.json")):
        data = load_json(path)
        original = copy.deepcopy(data)
        manufacturer = path.parts[-3]
        model = path.parts[-2]
        file_changed = False
        for record_id, record in records_from(data):
            stats["records_scanned"] += 1
            if enrich_record(record, manufacturer, model, blades, transponders, stats, conflicts, path, record_id):
                stats["records_changed"] += 1
                file_changed = True
        if file_changed and data != original:
            changed_files += 1
            if args.apply:
                write_json(path, data)

    stats["files_changed"] = changed_files
    stats["blade_catalogue_applications"] = len(blades)
    stats["transponder_catalogue_applications"] = len(transponders)
    stats["conflicts_total"] = len(conflicts)
    stats["mode_apply"] = int(args.apply)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **dict(sorted(stats.items())),
    }

    args.report_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.report_dir / "canonical_mapping_summary.json", summary)
    write_json(args.report_dir / "canonical_mapping_conflicts.json", conflicts)
    (args.report_dir / "canonical_mapping_report.md").write_text(
        summary_markdown(summary, conflicts), encoding="utf-8"
    )

    print(json.dumps(summary, indent=2))
    print(f"Conflict report: {args.report_dir / 'canonical_mapping_conflicts.json'}")
    if not args.apply:
        print("Dry-run only. Re-run with --apply to write changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
