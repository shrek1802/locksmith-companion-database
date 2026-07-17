#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORD = ROOT / "database" / "vehicles" / "ford"
REPORT = ROOT / "reports" / "ford_security_access_bulk_classify.json"
PLACEHOLDERS = {None, "", "verification_required", "research_required"}

changed = []
skipped = []

for path in sorted(FORD.glob("*/models.json")):
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        skipped.append({"path": str(path.relative_to(ROOT)), "reason": f"parse_error: {exc}"})
        continue

    dirty = False
    for item_key, item in data.get("items", {}).items():
        vi = item.get("vehicle_information", {})
        prog = vi.get("programming", {})
        current = prog.get("security_access")
        if current not in PLACEHOLDERS:
            continue

        vehicle = item.get("vehicle", {})
        year_to = vehicle.get("year_to")
        text = json.dumps(item, ensure_ascii=False).lower()
        online = str(prog.get("online_requirement", "")).lower()
        route = str(prog.get("route", "")).lower()
        immo = str(vi.get("immobiliser_system", "")).lower()
        variant = str(vehicle.get("variant", "")).lower()

        value = None
        basis = None

        # Explicit platform/service classifications only.
        if "meb" in text and ("volkswagen" in text or "vw" in text):
            value = "vw_meb_online_security_access"
            basis = "record explicitly identifies Volkswagen MEB-derived security architecture"
        elif "fdrs" in text or online in {"yes", "required", "normally yes", "online"}:
            value = "ford_fdrs_online_security_access"
            basis = "record explicitly identifies FDRS or required online programming"
        elif "vag-derived" in variant or "vag derived" in text:
            value = "vag_legacy_pin_or_security_access"
            basis = "record explicitly identifies a VAG-derived Ford generation"
        elif "no immobiliser" in text or "immobiliser not fitted" in text:
            value = "not_applicable_no_immobiliser"
            basis = "record explicitly states no immobiliser is fitted"
        elif "pats" in immo and ("obd" in route or "diagnostic" in route) and online in {"no", "normally no", "not normally", "offline"}:
            value = "tool_calculated_or_bypassed_pats"
            basis = "record explicitly identifies Ford PATS, diagnostic/OBD programming and no normal online requirement"
        elif "pats" in text and ("obd" in text or "diagnostic" in text) and isinstance(year_to, int) and year_to <= 2023 and "fdrs" not in text:
            value = "tool_calculated_or_bypassed_pats"
            basis = "record identifies Ford PATS diagnostic programming and contains no FDRS marker"

        if value is None:
            skipped.append({
                "path": str(path.relative_to(ROOT)),
                "item_key": item_key,
                "record_id": item.get("record_id"),
                "reason": "insufficient explicit evidence for automatic classification"
            })
            continue

        prog["security_access"] = value
        verification = item.setdefault("verification", {})
        verification["security_access_status"] = "classified_from_existing_record_evidence"
        verification["security_access_basis"] = basis
        verification["security_access_classifier"] = "ford_security_access_bulk_classify_v1"
        changed.append({
            "path": str(path.relative_to(ROOT)),
            "item_key": item_key,
            "record_id": item.get("record_id"),
            "value": value,
            "basis": basis
        })
        dirty = True

    if dirty:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps({
    "policy": "Classify only when the existing Ford record explicitly identifies the security architecture or access route; ambiguous records remain untouched.",
    "changed_count": len(changed),
    "skipped_count": len(skipped),
    "changed": changed,
    "skipped": skipped
}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"Changed {len(changed)} records; skipped {len(skipped)} records")
