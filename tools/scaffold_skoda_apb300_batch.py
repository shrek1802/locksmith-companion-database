#!/usr/bin/env python3
"""Create initial UK/RHD Škoda records from official UK and Autel evidence."""

from __future__ import annotations

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT/"database"/"vehicles"/"skoda"
UK="https://www.skoda.co.uk/"; AUTEL="https://www.autel.com/u/cms/www/202602/12012616q4ru.pdf"
MODELS={"fabia":("Fabia","2015-2021"),"karoq":("Karoq","2018-2022"),"kodiaq":("Kodiaq","2017-2021"),"octavia":("Octavia","2013-2021"),"rapid":("Rapid","2013-2021"),"superb":("Superb","2015-2022"),"scala":("Scala","2019-2022")}

def write(path,data): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def create(mid,name,years):
    d=BASE/mid; files={k:f"{k}.json" for k in ("models","procedures","modules","wiring","service_functions","notes","photos")}
    write(d/"manifest.json",{"schema_version":"2.1","updated_at":"2026-07-18","manufacturer":{"id":"skoda","name":"Škoda"},"model":{"id":mid,"name":name},"version":1,"files":files,"verification":{"status":"research_in_progress","market":"UK","drive_side":"RHD"}})
    write(d/"models.json",{"schema_version":"2.1","model":name,"market":"UK","drive_side":"RHD","generations":[{"id":f"{mid}_apb300_scope","name":f"{name} APB300 coverage range","years":years,"platform":"Volkswagen Group MQB per official Autel coverage category","immobiliser_family":"Exact dashboard/key family requires fitted-hardware confirmation","key_variants":[{"type":"keyed","status":"research_required"},{"type":"KESSY_or_keyless","status":"research_required"}],"status":"partially_verified"}],"sources":{"skoda_uk":{"publisher":"Škoda UK","title":"UK model range","url":UK,"supports":["UK market presence"]},"autel":{"publisher":"Autel","title":"APB300 coverage","url":AUTEL,"supports":[f"Škoda {name} {years} working-key Add Key"]}}})
    write(d/"procedures.json",{"schema_version":"2.1","model":name,"procedures":[{"id":"add_key","name":"Add key","method":"Read immobiliser data from opened working key with APB300 and prepare supported replacement","status":"partially_verified","tool_support":[{"tool":"Autel APB300 with MaxiIM 508/608 series","status":"partially_verified","confidence":"high","coverage":f"Škoda {name} {years}","source":AUTEL,"working_key_required":True,"vehicle_connection_required":False,"required_hardware":["APB300","Compatible MaxiIM tablet","Supported Autel IKEY or PCB"],"limits":"Add Key only; exact keyed/KESSY variant and key PCB require confirmation."}]},{"id":"akl","name":"All keys lost","method":"No AKL support inferred from working-key coverage","status":"research_required"}]})
    write(d/"modules.json",{"schema_version":"2.1","model":name,"modules":[{"id":"instrument_cluster","name":"Instrument cluster","role":"Fitted MQB dashboard dependent","location":"UK RHD location not verified","status":"research_required"},{"id":"kessy","name":"KESSY/access-start","role":"Only where fitted","location":"UK RHD location not verified","status":"research_required"},{"id":"gateway","name":"Gateway","role":"Exact security role not verified","location":"UK RHD location not verified","status":"research_required"}]})
    write(d/"wiring.json",{"schema_version":"2.1","model":name,"connections":[{"id":"obd","name":"OBD-II connector","location":"UK RHD location not verified","status":"research_required"},{"id":"bench","name":"Bench connection","notes":"No pinout, processor, EEPROM or adapter claim without exact hardware evidence.","status":"research_required"}]})
    write(d/"service_functions.json",{"schema_version":"2.1","model":name,"functions":[{"id":"key_count","name":"Read learned key count","availability":"Exact dashboard/tool dependent","status":"research_required"}]})
    write(d/"notes.json",{"schema_version":"2.1","model":name,"notes":[{"title":"Scope","text":"Škoda UK confirms UK presence; Autel confirms only APB300 working-key Add Key coverage for stated years."},{"title":"Reuse","text":"MQB is reused at architecture level only; no Volkswagen/SEAT RHD location, wiring or AKL route is inherited."}],"status":"research_in_progress"})
    write(d/"photos.json",{"schema_version":"2.1","model":name,"photos":[],"required":["UK RHD OBD location","Dashboard/KESSY locations","Keyed/keyless key examples"],"status":"awaiting_verified_images"})

def main():
    for mid,(name,years) in MODELS.items(): create(mid,name,years)
    write(BASE/"manifest.json",{"schema_version":"2.1","updated_at":"2026-07-18","manufacturer":{"id":"skoda","name":"Škoda","market":"UK","drive_side":"RHD"},"version":1,"models":{mid:{"name":name,"version":1,"manifest":f"{mid}/manifest.json","status":"research_in_progress"} for mid,(name,_) in MODELS.items()},"status":"research_in_progress","sources":{"skoda_uk":{"publisher":"Škoda UK","title":"UK model range","url":UK,"supports":["UK model presence"]},"autel":{"publisher":"Autel","title":"APB300 coverage","url":AUTEL,"supports":["Working-key Add Key coverage"]}}})
    for p in (ROOT/"manifest.json",ROOT/"database"/"manifest.json"):
        x=json.loads(p.read_text(encoding="utf-8")); x["manufacturers"]["skoda"]={"name":"Škoda","version":1,"manifest":"database/vehicles/skoda/manifest.json","status":"research_in_progress","updated_at":"2026-07-18"}; write(p,x)
    print("created Škoda APB300 batch")
    return 0

if __name__=="__main__": raise SystemExit(main())
