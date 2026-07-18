#!/usr/bin/env python3
"""Create conservative UK/RHD CUPRA architecture records from official evidence."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "database" / "vehicles" / "cupra"
TODAY = "2026-07-18"
UK_RANGE = "https://www.cupraofficial.co.uk/new-cars"
UK_MANUALS = "https://www.cupraofficial.co.uk/owners/technical-support/cupra-car-manuals"
VW_2020 = "https://www.volkswagen-group.com/en/publications/more/seat-annual-report-2020-3199/download?disposition=attachment"
VW_2021 = "https://www.volkswagen-group.com/en/publications/corporate/seat-annual-report-2021-1908/download?disposition=attachment"
VW_BORN = "https://www.volkswagen-group.com/en/press-releases/ceo-herbert-diess-at-the-annual-general-meeting-with-new-auto-volkswagen-will-be-reinvented-16774"
VW_RAVAL = "https://annualreport2025.volkswagen-group.com/group-management-report/report-on-expected-developments/model-innovations-in-2026.html"

# Platform wording is included only where the cited official Group source names it.
MODELS = {
    "ateca": ("Ateca", "CUPRA-era UK model", "Volkswagen Group MQB family; exact revision requires VIN/build confirmation", UK_RANGE, "partially_verified"),
    "born": ("Born", "2021-present", "Volkswagen Group MEB", VW_BORN, "partially_verified"),
    "formentor": ("Formentor", "2020-present", "Volkswagen Group MQB Evo production family", VW_2020, "partially_verified"),
    "leon": ("Leon", "2020-present", "Volkswagen Group MQB Evo", VW_2020, "partially_verified"),
    "leon_estate": ("Leon Estate", "2020-present", "Volkswagen Group MQB Evo", VW_2020, "partially_verified"),
    "tavascan": ("Tavascan", "2024-present", "Volkswagen Group MEB", VW_2021, "partially_verified"),
    "terramar": ("Terramar", "2024-present", "Platform designation requires a directly naming source", UK_RANGE, "research_required"),
    "raval": ("Raval", "2026-present", "Volkswagen Group MEB+", VW_RAVAL, "partially_verified"),
}


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def create(model_id: str, name: str, years: str, platform: str, platform_source: str, status: str) -> None:
    folder = BASE / model_id
    files = {key: f"{key}.json" for key in ("models", "procedures", "modules", "wiring", "service_functions", "notes", "photos")}
    write(folder / "manifest.json", {"schema_version":"2.1","updated_at":TODAY,"manufacturer":{"id":"cupra","name":"CUPRA"},"model":{"id":model_id,"name":name},"version":1,"files":files,"verification":{"status":"research_in_progress","market":"UK","drive_side":"RHD"}})
    write(folder / "models.json", {"schema_version":"2.1","model":name,"market":"UK","drive_side":"RHD","generations":[{"id":f"{model_id}_uk","name":f"{name} UK architecture","years":years,"platform":platform,"immobiliser_family":"Exact fitted immobiliser and dashboard family not verified","key_variants":[{"type":"keyed","applicability":"Where fitted; not inferred from sibling models","status":"research_required"},{"type":"keyless_or_proximity","applicability":"Where fitted; separate from keyed systems","status":"research_required"}],"status":status}],"sources":{"cupra_uk":{"publisher":"CUPRA UK","title":"UK model range and owner manuals","url":UK_RANGE,"checked_at":TODAY,"confidence":"high","supports":["UK model presence"]},"platform":{"publisher":"Volkswagen Group or CUPRA UK","title":"Model/platform evidence","url":platform_source,"checked_at":TODAY,"confidence":"high" if status == "partially_verified" else "medium","supports":[platform]}}})
    write(folder / "procedures.json", {"schema_version":"2.1","model":name,"procedures":[{"id":"add_key_keyed","name":"Add key - keyed","method":"No model-specific supported procedure recorded","status":"research_required"},{"id":"add_key_proximity","name":"Add key - keyless/proximity","method":"No model-specific supported procedure recorded","status":"research_required"},{"id":"akl_keyed","name":"All keys lost - keyed","method":"No model-specific supported procedure recorded","status":"research_required"},{"id":"akl_proximity","name":"All keys lost - keyless/proximity","method":"No model-specific supported procedure recorded","status":"research_required"}]})
    write(folder / "modules.json", {"schema_version":"2.1","model":name,"modules":[{"id":"immobiliser","name":"Immobiliser-authorisation system","role":"Exact controller topology requires fitted-hardware evidence","location":"UK RHD location not verified","status":"research_required"},{"id":"access_start","name":"Access/start or KESSY-equivalent controller","role":"Keyless/proximity variant only where fitted","location":"UK RHD location not verified","status":"research_required"},{"id":"gateway","name":"Gateway","role":"Security role not inferred from platform siblings","location":"UK RHD location not verified","status":"research_required"}]})
    write(folder / "wiring.json", {"schema_version":"2.1","model":name,"connections":[{"id":"obd","name":"OBD-II connector","location":"UK RHD location not verified","status":"research_required"},{"id":"bench","name":"Bench connection","notes":"No wiring, pinout, EEPROM, MCU, processor or adapter data verified.","status":"research_required"}]})
    write(folder / "service_functions.json", {"schema_version":"2.1","model":name,"functions":[{"id":"key_learning","name":"Key learning","availability":"No CUPRA model-specific tool coverage verified","status":"research_required"},{"id":"key_count","name":"Read learned key count","availability":"Controller and tool dependent","status":"research_required"}]})
    write(folder / "notes.json", {"schema_version":"2.1","model":name,"notes":[{"title":"Evidence boundary","text":"Official sources support UK model presence and, where stated, platform only. No SEAT or Volkswagen locksmith procedure is inherited without explicit CUPRA/model evidence."},{"title":"Variant separation","text":"Keyed and keyless/proximity routes are separate. Applicability, key type, blade, frequency and transponder remain research_required."},{"title":"Workshop verification","text":"Capture VIN/build date, UK RHD locations, key part number and fitted controller identifiers before promoting technical fields."}],"status":"research_in_progress"})
    write(folder / "photos.json", {"schema_version":"2.1","model":name,"photos":[],"required":["UK RHD OBD location","Fitted immobiliser/access-start modules","Keyed and proximity key examples with part numbers"],"status":"awaiting_verified_images"})


def main() -> int:
    for model_id, values in MODELS.items():
        create(model_id, *values)
    write(BASE / "manifest.json", {"schema_version":"2.1","updated_at":TODAY,"manufacturer":{"id":"cupra","name":"CUPRA","market":"UK","drive_side":"RHD"},"version":1,"models":{model_id:{"name":values[0],"version":1,"manifest":f"{model_id}/manifest.json","status":"research_in_progress"} for model_id,values in MODELS.items()},"status":"research_in_progress","sources":{"uk_range":{"publisher":"CUPRA UK","url":UK_RANGE},"uk_manuals":{"publisher":"CUPRA UK","url":UK_MANUALS}}})
    for path in (ROOT / "manifest.json", ROOT / "database" / "manifest.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        data["manufacturers"]["cupra"] = {"name":"CUPRA","version":1,"manifest":"database/vehicles/cupra/manifest.json","status":"research_in_progress","updated_at":TODAY}
        write(path, data)
    print(f"created CUPRA UK batch ({len(MODELS)} models)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
