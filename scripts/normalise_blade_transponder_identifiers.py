#!/usr/bin/env python3
"""Normalise blade/transponder identifiers using only recorded canonical evidence."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-07-19"
UNKNOWN = {None, "", "research_required", "transponder_unknown"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def records(data: dict):
    for value in data.get("items", {}).values():
        yield value.get("vehicle_information", value)
    for value in data.get("generations", []):
        yield value.get("vehicle_information", value)


def blade_batch() -> dict:
    path = ROOT / "database/reference/uk_blade_catalogue.json"
    catalogue = load(path)
    source_ids = set(catalogue.get("sources", {}))
    displays = {}
    for family_id, item in catalogue["items"].items():
        display = item["display_name"].upper()
        item["canonical_id"] = display
        item.setdefault("cut_type", "research_required")
        item["aliases"] = sorted(set(item.get("aliases", [])) | {display, family_id})
        item["evidence"] = [sid for sid in item.get("evidence_source_ids", []) if sid in source_ids]
        item["confidence"] = "high" if item.get("status") == "catalogue_supported" and item["evidence"] else "research_required"
        item.setdefault("notes", "Catalogue identifier is canonical; vehicle and key-variant applicability remains application-specific.")
        displays[display] = family_id
    catalogue["updated_at"] = DATE
    save(path, catalogue)

    stats = Counter()
    for model_path in sorted((ROOT / "database/vehicles").glob("*/*/models.json")):
        data = load(model_path)
        changed = False
        for info in records(data):
            profile = info.get("blade_profile")
            blade_id = info.get("blade_id")
            canonical = catalogue["items"].get(str(blade_id).lower()) if blade_id else None
            if canonical:
                wanted = canonical["canonical_id"]
                if profile != wanted:
                    info["blade_profile"] = wanted
                    stats["blade_values_normalised"] += 1
                    changed = True
                continue
            if isinstance(profile, str) and profile.upper() in displays:
                family_id = displays[profile.upper()]
                if info.get("blade_id") != family_id:
                    info["blade_id"] = family_id
                    stats["blade_references_added"] += 1
                    changed = True
                if profile != catalogue["items"][family_id]["canonical_id"]:
                    info["blade_profile"] = catalogue["items"][family_id]["canonical_id"]
                    stats["blade_values_normalised"] += 1
                    changed = True
                continue
            if profile not in (None, "research_required"):
                candidates = sorted({m.lower() for m in re.findall(r"\b[A-Z]{2,4}\d{1,3}[A-Z]?\b", profile.upper()) if m in displays})
                if candidates:
                    old = info.setdefault("blade_transition_candidates", [])
                    merged = sorted(set(old) | set(candidates))
                    if merged != old:
                        info["blade_transition_candidates"] = merged
                info["blade_profile"] = "research_required"
                info["blade_id"] = None
                verification = info.setdefault("blade_verification", {})
                verification.update({"status": "research_required", "confidence": "conflicting_or_noncanonical_value", "last_checked": DATE})
                stats["blade_values_quarantined"] += 1
                changed = True
        if changed:
            save(model_path, data)
            stats["blade_files_updated"] += 1
    return dict(stats)


def canonical_transponder_id(item: dict) -> str:
    code = item.get("silca_code", "")
    match = re.search(r"(?:ID|\s)([0-9A-F]{2}(?:-[0-9A-F]{2})?)$", code.upper())
    value = match.group(1) if match else ""
    if code.startswith("TEX/CR") and value:
        return f"4D{value}"
    if code == "TEXAS 4C":
        return "4C"
    if value:
        return f"ID{value}"
    return "research_required"


def technology(item: dict) -> str:
    code = item.get("silca_code", "")
    return (
        "Megamos AES" if "AES" in item.get("display_name", "").upper() else
        "Megamos Crypto" if code.startswith("MEG/CR") else
        "Megamos fixed code" if code.startswith("MEG ") else
        "Philips Crypto / Hitag" if code.startswith("PH/CR") else
        "Philips fixed code" if code.startswith("PH ") else
        "Texas Crypto 4D" if code.startswith("TEX/CR") else
        "Texas fixed code" if code == "TEXAS 4C" else
        "Temic fixed code" if code.startswith("TEMIC") else
        "Sokymat Crypto" if code.startswith("SOK/CR") else
        "research_required"
    )


def transponder_batch() -> dict:
    path = ROOT / "database/reference/uk_transponder_catalogue.json"
    catalogue = load(path)
    sources = set(catalogue.get("sources", {}))
    by_legacy = {}
    for family_id, item in catalogue["items"].items():
        canonical = canonical_transponder_id(item)
        item["canonical_id"] = canonical
        item["technology_family"] = technology(item)
        item["chip_or_ic"] = None
        item["aliases"] = sorted(set(item.get("aliases", [])) | {x for x in (canonical, item.get("silca_code"), item.get("display_name"), family_id) if x and x != "research_required"})
        item["evidence"] = [sid for sid in item.get("evidence_source_ids", []) if sid in sources]
        item.setdefault("notes", "Catalogue family identifier does not imply one physical chip or integrated remote IC.")
        for legacy in (family_id, item.get("repository_transponder_id")):
            if legacy:
                by_legacy[legacy] = item
        if family_id == "texas_crypto_id63":
            item["identifier_variants"] = ["4D63-40", "4D63-80"]
            item["notes"] = "The 40-bit and 80-bit implementations must remain distinct where recorded; generic 4D63 does not establish bit length."
    catalogue["updated_at"] = DATE
    save(path, catalogue)

    stats = Counter()
    for model_path in sorted((ROOT / "database/vehicles").glob("*/*/models.json")):
        data = load(model_path)
        changed = False
        for info in records(data):
            old_id = info.get("transponder_id")
            legacy_id = info.get("transponder_family_id") or old_id
            verification = info.get("transponder_verification", {})
            canonical_family = verification.get("canonical_transponder_family_id") if isinstance(verification, dict) else None
            exact_63 = {"texas_4d63_40bit": "4D63-40", "texas_4d63_80bit": "4D63-80"}.get(legacy_id)
            if exact_63:
                aliases = [exact_63, exact_63.replace("-", " "), "Texas Crypto 4D"]
                updates = {
                    "transponder_family_id": legacy_id,
                    "transponder_id": exact_63,
                    "technology_family": "Texas Crypto 4D",
                    "chip_or_ic": None,
                    "transponder_aliases": aliases,
                }
                for key, value in updates.items():
                    if info.get(key) != value:
                        info[key] = value
                        changed = True
                        stats["transponder_63_variants_preserved"] += 1
                continue
            if old_id == "transponder_unknown":
                info["transponder_family_id"] = old_id
                info["transponder_id"] = "research_required"
                info.setdefault("technology_family", "research_required")
                info["chip_or_ic"] = None
                info.setdefault("transponder_aliases", [])
                stats["transponder_values_quarantined"] += 1
                changed = True
                continue
            item = by_legacy.get(canonical_family) or by_legacy.get(old_id)
            if item and item["canonical_id"] != "research_required":
                if old_id != item["canonical_id"]:
                    info["transponder_family_id"] = old_id
                    info["transponder_id"] = item["canonical_id"]
                    stats["transponder_ids_normalised"] += 1
                    changed = True
                for key, value in (("technology_family", item["technology_family"]), ("chip_or_ic", None), ("transponder_aliases", item["aliases"])):
                    if info.get(key) != value:
                        info[key] = value
                        stats["transponder_structured_fields_updated"] += 1
                        changed = True
            elif old_id not in UNKNOWN and not re.fullmatch(r"(?:ID)?[0-9A-F]{2}(?:-[0-9A-F]{2})?|4D[0-9A-F]{2}(?:-(?:40|80))?", str(old_id), re.I):
                info["transponder_family_id"] = old_id
                info["transponder_id"] = "research_required"
                info.setdefault("technology_family", info.get("transponder_type") or "research_required")
                info["chip_or_ic"] = None
                info.setdefault("transponder_aliases", [])
                verify = info.setdefault("transponder_verification", {})
                verify.update({"status": "research_required", "confidence": "canonical_identifier_not_supported", "last_checked": DATE})
                stats["transponder_values_quarantined"] += 1
                changed = True
        if changed:
            save(model_path, data)
            stats["transponder_files_updated"] += 1
    return dict(stats)


def main() -> None:
    report_path = ROOT / "reports/blade_transponder_identifier_normalisation_audit.json"
    previous = load(report_path) if report_path.exists() else {}
    blade = blade_batch()
    transponder = transponder_batch()
    for section, current in (("blade", blade), ("transponder", transponder)):
        for key, value in previous.get(section, {}).items():
            if isinstance(value, int):
                current[key] = current.get(key, 0) + value
    report = {
        "schema_version": "2.1",
        "updated_at": DATE,
        "category": "blade_transponder_identifier_normalisation_audit",
        "method": "Deterministic normalisation using only existing canonical catalogues and recorded evidence; no new vehicle research.",
        "blade": blade,
        "transponder": transponder,
    }
    save(report_path, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
