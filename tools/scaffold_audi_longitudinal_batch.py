#!/usr/bin/env python3
"""Create UK/RHD Audi longitudinal-platform records with scoped BCM2 evidence."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDI = ROOT / "database" / "vehicles" / "audi"

MODELS = {
    "a4": ("A4", [("b5","B5","1995-2001"),("b6","B6","2001-2005"),("b7","B7","2005-2008"),("b8","B8","2008-2015"),("b9","B9","2015-2024")]),
    "a5": ("A5", [("8t","8T","2007-2016"),("f5","F5","2016-2024")]),
    "a6": ("A6", [("c5","C5","1997-2004"),("c6","C6","2004-2011"),("c7","C7","2011-2018"),("c8","C8","2018-2025")]),
    "a7": ("A7", [("4g8","4G8","2010-2018"),("4k8","4K8","2018-present")]),
    "a8": ("A8", [("d2","D2","1994-2002"),("d3","D3","2002-2010"),("d4","D4","2010-2017"),("d5","D5","2017-present")]),
    "q5": ("Q5", [("8r","8R","2008-2017"),("fy","FY","2017-2024"),("gu","GU","2024-present")]),
    "q7": ("Q7", [("4l","4L","2006-2015"),("4m","4M","2015-present")]),
    "q8": ("Q8", [("4m8","4M8","2018-present")]),
}

ABRITES_URL = "https://abrites.com/media/user_manuals/html/abrites-diagnostics-for-vag-online-user-manual/index.html"
AUDI_UK_URL = "https://press.audi.co.uk/models/concept/releases"


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def is_bcm2_scope(model_id: str, code: str) -> bool:
    return (model_id in {"a4", "a5", "q5"} and code in {"b8", "8t", "8r"}) or (
        model_id in {"a6", "a7", "a8"} and code in {"c7", "4g8", "d4"}
    )


def create(model_id: str, name: str, generations: list[tuple[str,str,str]]) -> None:
    folder = AUDI / model_id
    files = {key: f"{key}.json" for key in ("models","procedures","modules","wiring","service_functions","notes","photos")}
    write(folder/"manifest.json", {"schema_version":"2.1","updated_at":"2026-07-18","manufacturer":{"id":"audi","name":"Audi"},"model":{"id":model_id,"name":name},"version":1,"files":files,"verification":{"status":"research_in_progress","market":"UK","drive_side":"RHD"}})
    rows=[]
    for code,label,years in generations:
        bcm2=is_bcm2_scope(model_id,code)
        rows.append({"id":code,"name":f"{name} {label}","years":years,"platform":"Audi longitudinal architecture; exact platform revision requires generation evidence","immobiliser_family":"BCM2 / Immo V" if bcm2 else "Exact family requires generation and fitted-hardware evidence","key_variants":[{"type":"keyed","status":"research_required"},{"type":"advanced_key_or_keyless","status":"research_required"}],"status":"partially_verified" if bcm2 else "research_in_progress","verification_scope":"Abrites identifies this model/era within BCM2 coverage; exact vehicle hardware, UK specification and location remain unverified." if bcm2 else "UK model history only."})
    write(folder/"models.json", {"schema_version":"2.1","model":name,"market":"UK","drive_side":"RHD","generations":rows,"sources":{"audi_uk_archive":{"publisher":"Audi UK Newsroom","title":"UK current and previous model archive","url":AUDI_UK_URL,"supports":["UK model presence"]},"abrites_vag_online":{"publisher":"Abrites","title":"Diagnostics for VAG Online user manual","url":ABRITES_URL,"supports":["BCM2 application scope and operation constraints for named Audi models"]}}})
    if model_id in {"a4","a5","q5"}:
        akl="Abrites documents BCM2 AKL by making a dealer key then learning keys for A4/A5/Q5; exact supported vehicle and prerequisites must be confirmed in current software."
    elif model_id in {"a6","a7","a8"}:
        akl="Abrites documents conditional BCM2 AKL when ECU/TCU component security can be read for A6/A7/A8."
    else:
        akl="No model-wide AKL route verified."
    write(folder/"procedures.json", {"schema_version":"2.1","model":name,"procedures":[{"id":"add_key","name":"Add key","method":"Generation and fitted-system specific","tool_support":[{"tool":"Abrites VAG Online","status":"partially_verified" if model_id in {"a4","a5","a6","a7","a8","q5"} else "research_required","source":ABRITES_URL,"notes":"Manual covers named platform families; verify exact vehicle and active licence."}],"status":"partially_verified" if model_id in {"a4","a5","a6","a7","a8","q5"} else "research_in_progress"},{"id":"akl","name":"All keys lost","method":akl,"required_adapters":"PROTAG ZN003/ZN002 is stated for supported key programming; additional AKL cables may be required and must be checked for the exact job.","status":"partially_verified" if model_id in {"a4","a5","a6","a7","a8","q5"} else "research_in_progress"}]})
    write(folder/"modules.json", {"schema_version":"2.1","model":name,"modules":[{"id":"bcm2_or_access_start","name":"BCM2/access-start","role":"Immobiliser module on covered generations; otherwise generation dependent","location":"UK RHD location not verified","status":"partially_verified" if model_id in {"a4","a5","a6","a7","a8","q5"} else "research_in_progress"},{"id":"gateway","name":"Gateway","role":"Security/diagnostic role generation dependent","location":"UK RHD location not verified","status":"research_in_progress"}]})
    write(folder/"wiring.json", {"schema_version":"2.1","model":name,"connections":[{"id":"obd","name":"OBD-II connector","location":"UK RHD location not verified","status":"research_in_progress"},{"id":"bench","name":"Bench connection","notes":"No pinout stored. Use exact current tool diagram and module part number.","status":"research_in_progress"}]})
    write(folder/"service_functions.json", {"schema_version":"2.1","model":name,"functions":[{"id":"key_learning","name":"Key learning","availability":"Abrites documents guided functions for supported platforms; exact vehicle coverage required","status":"partially_verified" if model_id in {"a4","a5","a6","a7","a8","q5"} else "research_in_progress"}]})
    write(folder/"notes.json", {"schema_version":"2.1","model":name,"notes":[{"title":"Evidence scope","text":"Audi UK confirms model presence; Abrites confirms only the named BCM2/tool scope. No RHD location or wiring is inherited."},{"title":"Key variants","text":"Keyed and advanced-key/keyless records require separate exact-generation evidence."}],"status":"research_in_progress"})
    write(folder/"photos.json", {"schema_version":"2.1","model":name,"photos":[],"required":["UK RHD OBD location","BCM2/access-start location","Key variants"],"status":"awaiting_verified_images"})


def main() -> int:
    for model_id,(name,gens) in MODELS.items(): create(model_id,name,gens)
    manifest_path=AUDI/"manifest.json"; manifest=json.loads(manifest_path.read_text(encoding="utf-8")); manifest["version"]=3; manifest["updated_at"]="2026-07-18"
    for model_id,(name,_) in MODELS.items(): manifest["models"][model_id]={"name":name,"version":1,"manifest":f"{model_id}/manifest.json","status":"research_in_progress"}
    write(manifest_path,manifest)
    for path in (ROOT/"manifest.json",ROOT/"database"/"manifest.json"):
        data=json.loads(path.read_text(encoding="utf-8")); data["manufacturers"]["audi"].update({"version":3,"updated_at":"2026-07-18"}); write(path,data)
    print("created Audi longitudinal batch")
    return 0


if __name__=="__main__": raise SystemExit(main())
