#!/usr/bin/env python3
"""Create initial UK/RHD SEAT records from official UK and Autel evidence."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEAT = ROOT / "database" / "vehicles" / "seat"
SOURCE_UK = "https://www.seat.co.uk/"
SOURCE_HISTORY = "https://www.seat.co.uk/about-seat/news-events/corporate/70-years-of-history"
SOURCE_AUTEL = "https://www.autel.com/u/cms/www/202602/12012616q4ru.pdf"
MODELS = {
    "arona": ("Arona", "2018-2021"),
    "ateca": ("Ateca", "2017-2021"),
    "ibiza": ("Ibiza", "2018-2021"),
    "leon": ("Leon", "2017-2021"),
    "tarraco": ("Tarraco", "2019-2021"),
    "toledo": ("Toledo", "2016-2019"),
}


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def create(model_id: str, name: str, coverage: str) -> None:
    folder = SEAT / model_id
    files = {key: f"{key}.json" for key in ("models","procedures","modules","wiring","service_functions","notes","photos")}
    write(folder/"manifest.json", {"schema_version":"2.1","updated_at":"2026-07-18","manufacturer":{"id":"seat","name":"SEAT"},"model":{"id":model_id,"name":name},"version":1,"files":files,"verification":{"status":"research_in_progress","market":"UK","drive_side":"RHD"}})
    write(folder/"models.json", {"schema_version":"2.1","model":name,"market":"UK","drive_side":"RHD","generations":[{"id":f"{model_id}_apb300_scope","name":f"{name} APB300 coverage range","years":coverage,"platform":"Volkswagen Group MQB per official Autel coverage category","immobiliser_family":"Exact MQB dashboard/key family requires fitted-hardware confirmation","key_variants":[{"type":"keyed","status":"research_required"},{"type":"KESSY_or_keyless","status":"research_required"}],"status":"partially_verified"}],"sources":{"seat_uk":{"publisher":"SEAT UK","title":"UK model range and history","url":SOURCE_UK,"supports":["UK market presence"]},"autel_apb300":{"publisher":"Autel","title":"APB300 Volkswagen Group MLB and MQB coverage","url":SOURCE_AUTEL,"supports":[f"SEAT {name} {coverage} working-key Add Key coverage"]}}})
    write(folder/"procedures.json", {"schema_version":"2.1","model":name,"procedures":[{"id":"add_key","name":"Add key","method":"Read immobiliser data from the opened original working key with APB300; prepare a supported replacement key/PCB","status":"partially_verified","tool_support":[{"tool":"Autel APB300 with MaxiIM 508/608 series","status":"partially_verified","confidence":"high","coverage":f"SEAT {name} {coverage}","source":SOURCE_AUTEL,"working_key_required":True,"vehicle_connection_required":False,"required_hardware":["Autel APB300","Compatible MaxiIM tablet","Supported Autel IKEY or key PCB"],"limits":"Add Key only; keyed/KESSY applicability and exact key PCB must be confirmed."}]},{"id":"akl","name":"All keys lost","method":"No AKL support is inferred from APB300 working-key coverage","status":"research_required"}]})
    write(folder/"modules.json", {"schema_version":"2.1","model":name,"modules":[{"id":"instrument_cluster","name":"Instrument cluster","role":"MQB immobiliser role depends on fitted dashboard","location":"UK RHD location not verified","status":"research_required"},{"id":"kessy_or_access_start","name":"KESSY/access-start","role":"Only applicable where fitted","location":"UK RHD location not verified","status":"research_required"},{"id":"gateway","name":"Gateway","role":"Exact security role not verified","location":"UK RHD location not verified","status":"research_required"}]})
    write(folder/"wiring.json", {"schema_version":"2.1","model":name,"connections":[{"id":"obd","name":"OBD-II connector","location":"UK RHD location not verified","status":"research_required"},{"id":"bench","name":"Bench connection","notes":"No wiring, processor, EEPROM or adapter claim without exact dashboard evidence.","status":"research_required"}]})
    write(folder/"service_functions.json", {"schema_version":"2.1","model":name,"functions":[{"id":"key_count","name":"Read learned key count","availability":"Exact dashboard/tool dependent","status":"research_required"}]})
    write(folder/"notes.json", {"schema_version":"2.1","model":name,"notes":[{"title":"Evidence scope","text":"SEAT UK sources confirm UK presence; Autel confirms only APB300 working-key Add Key coverage for the stated years."},{"title":"Variant policy","text":"Keyed and KESSY/keyless variants remain separate and unresolved until exact key/dashboard evidence is recorded."},{"title":"Shared architecture","text":"MQB context is reused only at platform level; no Volkswagen RHD location, wiring or AKL procedure is inherited."}],"status":"research_in_progress"})
    write(folder/"photos.json", {"schema_version":"2.1","model":name,"photos":[],"required":["UK RHD OBD location","Dashboard and KESSY locations where fitted","Keyed and keyless key examples"],"status":"awaiting_verified_images"})


def main() -> int:
    for model_id,(name,coverage) in MODELS.items(): create(model_id,name,coverage)
    write(SEAT/"manifest.json", {"schema_version":"2.1","updated_at":"2026-07-18","manufacturer":{"id":"seat","name":"SEAT","market":"UK","drive_side":"RHD"},"version":1,"models":{model_id:{"name":name,"version":1,"manifest":f"{model_id}/manifest.json","status":"research_in_progress"} for model_id,(name,_) in MODELS.items()},"status":"research_in_progress","sources":{"seat_uk_history":{"publisher":"SEAT UK","title":"70 years of SEAT history","url":SOURCE_HISTORY,"supports":["UK introduction and model history"]},"autel_apb300":{"publisher":"Autel","title":"APB300 Volkswagen Group coverage","url":SOURCE_AUTEL,"supports":["Working-key Add Key model/year coverage"]}}})
    for path in (ROOT/"manifest.json",ROOT/"database"/"manifest.json"):
        data=json.loads(path.read_text(encoding="utf-8")); data["manufacturers"]["seat"]={"name":"SEAT","version":1,"manifest":"database/vehicles/seat/manifest.json","status":"research_in_progress","updated_at":"2026-07-18"}; write(path,data)
    print("created SEAT APB300 batch")
    return 0


if __name__=="__main__": raise SystemExit(main())
