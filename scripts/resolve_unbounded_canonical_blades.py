#!/usr/bin/env python3
"""Add exact catalogue-backed generations where Phase 1 left years unbounded."""

import copy
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CAT=json.loads((ROOT/"database/reference/uk_blade_catalogue.json").read_text(encoding="utf-8"))

MAPPINGS={
 "database/vehicles/mini/clubman/models.json":[("r55_uk_2007_2014_slot","R55 UK slot-key generation",2007,2014,"hu200","slot_key",True,"https://www.press.bmwgroup.com/united-kingdom/article/detail/T0019712EN_GB/mini-clubman-to-lift-production-to-new-record-at-bmw-group-plant-oxford%3B-start-of-production-welcomed-by-rt-hon-stephen-timms-minister-for-competitiveness?language=en_GB")],
 "database/vehicles/mini/countryman/models.json":[("r60_uk_2010_2016_slot","R60 UK slot-key generation",2010,2016,"hu200","slot_key",True,"https://www.press.bmwgroup.com/united-kingdom/article/detail/T0084154EN_GB/mini-countryman-makes-its-uk-debut?language=en_GB")],
 "database/vehicles/mini/paceman/models.json":[("r61_uk_2012_2016_slot","R61 UK slot-key generation",2012,2016,"hu200","slot_key",False,None)],
 "database/vehicles/mini/roadster/models.json":[("r59_uk_2011_2015_proximity","R59 UK proximity/emergency-insert generation",2011,2015,"hu200","proximity",False,None)],
 "database/vehicles/smart/fortwo/models.json":[
   ("w450_uk_2000_2006_remote","450 remote-key generation",2000,2006,"ym23","remote_or_flip",True,None),
   ("w451_uk_2007_2013_remote","W451 remote-key generation",2007,2013,"va2","remote_or_flip",True,None),
   ("w453_uk_2014_2016_remote","453 remote-key generation",2014,2016,"va2","remote_or_flip",True,None)],
 "database/vehicles/smart/roadster/models.json":[("w452_uk_2003_2006_remote","452 remote-key generation",2003,2006,"ym23","remote_or_flip",False,None)],
 "database/vehicles/mercedes_benz/v_class/models.json":[("w638_uk_1996_2003_keyed","W638 keyed generation",1996,2003,"va5","keyed_or_remote",True,"https://mercedes-benz-publicarchive.com/marsClassic/en/instance/ko/638-series-V-Class-Multi-Purpose-Vehicles-1996---1999.xhtml?oid=5630")],
 "database/vehicles/mercedes_benz/sprinter/models.json":[("sprinter_1996_2014_ym15","Sprinter catalogue-supported keyed range",1996,2014,"ym15","keyed_or_remote",True,None)],
 "database/vehicles/mercedes_benz/vito/models.json":[("vito_1996_2014_ym15","Vito catalogue-supported keyed range",1996,2014,"ym15","keyed_or_remote",True,None)],
}

def app_end(app): return app["year_to"] if isinstance(app.get("year_to"),int) else (2025 if app["source_id"].endswith("2025") else 2014)

changed=[]; records=[]
for relative,mappings in MAPPINGS.items():
 path=ROOT/relative; data=json.loads(path.read_text(encoding="utf-8")); original=data["generations"][0]
 new=[]
 for record_id,name,start,end,family_id,variant,retain,oem_url in mappings:
  family=CAT["items"][family_id]
  apps=[a for a in family["applications"] if a["model_file"]==relative and a["year_from"]<=start and app_end(a)>=end]
  if not apps: raise ValueError(f"No full catalogue coverage for {record_id}")
  clone=copy.deepcopy(original); clone["id"]=record_id; clone["name"]=name; clone["years"]=f"{start}-{end}"
  clone["key_variants"]=[{"type":variant,"status":"partially_verified"}]
  clone["blade_profile"]=family["display_name"]; clone["blade_id"]=family_id
  source_ids=sorted({a["source_id"] for a in apps})
  evidence=[{"source_id":sid,"publisher":CAT["sources"][sid]["publisher"],"title":CAT["sources"][sid]["title"],"edition":CAT["sources"][sid]["edition"],"url":CAT["sources"][sid]["url"],"catalogue_rows":[a["catalogue_row"] for a in apps if a["source_id"]==sid]} for sid in source_ids]
  if oem_url: evidence.append({"source_id":"oem_generation_boundary","publisher":"Vehicle manufacturer archive","url":oem_url,"supports":"UK introduction or OEM generation boundary"})
  previous=clone.get("blade_verification",{}); old_evidence=previous.get("evidence",[]) if isinstance(previous,dict) else []
  clone["blade_verification"]={"status":"verified" if len(source_ids)>1 else "partially_verified","confidence":"high" if len(source_ids)>1 else "medium","last_checked":"2026-07-18","canonical_blade_family_id":family_id,"record_year_range":f"{start}-{end}","key_variant_scope":variant,"evidence":old_evidence+evidence}
  clone["catalogue_split"]={"origin_generation_id":original.get("id"),"boundary_basis":"Silca application range intersected with UK/OEM generation evidence where available","last_checked":"2026-07-18"}
  new.append(clone); records.append(record_id)
 if any(item[6] for item in mappings):
  remainder=copy.deepcopy(original); remainder["id"]=f"{original.get('id')}_other_generations_blade_research"; remainder["name"]=f"{original.get('name')} - other generations requiring blade evidence"; remainder["blade_profile"]="research_required"; remainder["blade_id"]=None; remainder["blade_verification"]={"status":"research_required","confidence":"outside_normalised_catalogue_range","last_checked":"2026-07-18"}; remainder["catalogue_split"]={"origin_generation_id":original.get("id"),"boundary_basis":"Retained for generations outside the exact catalogue/OEM mapping","last_checked":"2026-07-18"}; new.append(remainder)
 data["generations"]=new; path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"); changed.append(relative)
print(json.dumps({"changed_files":changed,"records":records},indent=2))
