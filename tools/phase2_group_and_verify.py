#!/usr/bin/env python3
"""Group Phase-2 architecture fields and apply evidence-bounded VAG/BMW reviews."""
from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; TODAY="2026-07-18"
VAG={"volkswagen","audi","seat","skoda","cupra"}; BMW={"bmw","mini"}
ROSS="https://wiki.ross-tech.com/wiki/index.php/Immobilizer"
PASSAT="https://wiki.ross-tech.com/wiki/index.php/VW_Passat_%283C%29_Immobilizer"
AUTEL="https://www.autel.com/u/cms/www/202602/12012616q4ru.pdf"
YANHUA="https://www.acdpmaster.com/en/Module.html"
YANHUA_FEM="https://blog.yanhuaacdp.com/yanhua-mini-acdp-program-bmw-fem-bdc-without-soldering/"
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def walk(o,path=()):
 if isinstance(o,dict):
  for k,v in o.items():yield from walk(v,path+(k,))
 elif isinstance(o,list):
  for v in o:yield from walk(v,path)
 else:yield path,o
def audit():
 dims={k:Counter() for k in ("manufacturer_group","platform","generation","immobiliser_family","dashboard_family","body_security_family","key_variant","transponder_family","blade_family","tool_support_family")}; cross=defaultdict(lambda:{"records":0,"manufacturers":set(),"models":set()}); files=0
 for p in (ROOT/"database"/"vehicles").glob("*/*/models.json"):
  files+=1; make=p.parts[-3]; model=p.parts[-2]; d=json.loads(p.read_text(encoding="utf-8")); dims["manufacturer_group"][make]+=1
  vals=list(walk(d)); found={k:set() for k in dims if k!="manufacturer_group"}
  for path,v in vals:
   key=".".join(path).lower(); s=str(v).strip()
   if not s or s.lower() in {"none","unknown"}:continue
   if "platform" in key:found["platform"].add(s)
   if "generation" in key and not key.endswith("generations"):found["generation"].add(s)
   if "immobiliser" in key or "immobilizer" in key:found["immobiliser_family"].add(s)
   if "dashboard" in key or "cluster" in key:found["dashboard_family"].add(s)
   if any(x in key for x in ("bcm","bsi","uch","fem","bdc","eis","ezs")):found["body_security_family"].add(s)
   if "variant" in key or key.endswith("type"): 
    if any(x in s.lower() for x in ("key","slot","proximity","kessy","smart")):found["key_variant"].add(s)
   if "transponder" in key:found["transponder_family"].add(s)
   if "blade" in key:found["blade_family"].add(s)
   if "tool" in key:found["tool_support_family"].add(s)
  for dim,ss in found.items():
   for s in ss:dims[dim][s]+=1
  fam=next(iter(found["immobiliser_family"]),"unclassified")
  plat=next(iter(found["platform"]),"unclassified")
  ck=f"{make}|{plat}|{fam}"; cross[ck]["records"]+=1;cross[ck]["manufacturers"].add(make);cross[ck]["models"].add(model)
 out={"schema_version":"1.0","generated_at":TODAY,"scope":"All UK/RHD model records","model_files":files,"dimensions":{k:[{"value":x,"records":n} for x,n in c.most_common()] for k,c in dims.items()},"architecture_groups":[{"group":k,"records":v["records"],"manufacturers":sorted(v["manufacturers"]),"models":sorted(v["models"])} for k,v in sorted(cross.items(),key=lambda x:-x[1]["records"])]}
 write(ROOT/"reports"/"phase2_shared_architecture_grouped_audit.json",out);print(f"grouped {files} model files into {len(cross)} architecture groups")
def add_note(make,text,sources):
 changed=0
 for p in (ROOT/"database"/"vehicles"/make).glob("*/notes.json"):
  d=json.loads(p.read_text(encoding="utf-8")); notes=d.get("notes")
  if not isinstance(notes,list):continue
  if any(n.get("title")=="Phase 2 shared-architecture review" for n in notes if isinstance(n,dict)):continue
  notes.append({"title":"Phase 2 shared-architecture review","text":text,"sources":sources,"confidence":"high for named family/tool scope; vehicle applicability remains generation-specific","checked_at":TODAY});write(p,d);changed+=1
 return changed
def vag():
 reg=json.loads((ROOT/"database"/"platforms"/"volkswagen"/"immobiliser_families.json").read_text(encoding="utf-8")); fam=reg["families"]
 # Official vendor claim: Module 44 supports VAG/Porsche 5C/5D add-key functions only.
 fam["vw_mqb_49_5c"]["tool_support"]=[{"tool":"Yanhua Mini ACDP/ACDP2 Module 44","operation":"add new key, add used key, modify original key ID","status":"manufacturer_confirmed","confidence":"high","source":YANHUA,"limits":"Does not establish vehicle applicability, AKL, wiring or adapter selection."}]
 fam["vw_mqb_49_5c"]["verification_state"]="partially_verified"
 fam["vw_mqb_49_5c"]["sources"]=[{"publisher":"Yanhua ACDP","title":"Module 44 VAG/Porsche 5C/5D IMMO","url":YANHUA,"supports":["named system tool scope"]}]
 write(ROOT/"database"/"platforms"/"volkswagen"/"immobiliser_families.json",reg)
 mapping={"vw_immo_2_3":("partially_verified",ROSS),"vw_immo_4a_adaptation":("partially_verified",ROSS),"vw_immo_4_challenge_or_45":("partially_verified",ROSS),"vw_immo_4_challenge":("partially_verified",ROSS),"vw_immo_4d_passat":("verified",PASSAT),"vw_mqb_49_5c":("partially_verified",YANHUA)}; upgraded=0
 for make in VAG:
  for p in (ROOT/"database"/"vehicles"/make).glob("*/models.json"):
   d=json.loads(p.read_text(encoding="utf-8")); dirty=False
   for item in d.get("items",{}).values():
    info=item.get("vehicle_information",{}); fid=info.get("immobiliser_family_id"); ver=item.get("verification",{})
    if fid in mapping and ver.get("status") in {"research_required","research_in_progress"}:
     ver["status"],src=mapping[fid]; ver.setdefault("evidence",[]).append({"scope":"shared immobiliser architecture only","source":src,"confidence":"high","checked_at":TODAY});dirty=True;upgraded+=1
   if dirty:write(p,d)
  add_note(make,"VAG family registry and official vendor material were checked. Keyed and KESSY remain separate; model-year, RHD location, AKL, wiring and exact dashboard applicability are not inherited.",[ROSS,PASSAT,AUTEL,YANHUA])
 print(f"VAG review upgraded {upgraded} architecture-scoped record statuses")
def bmw():
 data={"schema_version":"1.0","updated_at":TODAY,"manufacturer_group":["BMW","MINI"],"scope":"Shared family/tool verification; no chassis applicability inferred","families":{
 "ews":{"status":"research_required","vehicle_applicability":"generation-specific"},
 "cas2_cas3_cas3plus":{"status":"partially_verified","tool_support":[{"tool":"Yanhua ACDP Module 1","functions":["add_key","all_keys_lost","EEPROM/flash read-write"],"confidence":"high","source":YANHUA}],"vehicle_applicability":"research_required"},
 "cas4_cas4plus":{"status":"partially_verified","tool_support":[{"tool":"Yanhua ACDP Module 1","method":"in-circuit programming","functions":["add_key","all_keys_lost"],"confidence":"high","source":YANHUA}],"vehicle_applicability":"research_required"},
 "fem":{"status":"partially_verified","tool_support":[{"tool":"Yanhua ACDP Module 2","functions":["add_key","all_keys_lost","data backup/recovery"],"confidence":"high","source":YANHUA_FEM}],"vehicle_applicability":"research_required"},
 "bdc":{"status":"partially_verified","tool_support":[{"tool":"Yanhua ACDP Module 2","functions":["add_key","all_keys_lost","data backup/recovery"],"confidence":"high","source":YANHUA_FEM}],"vehicle_applicability":"research_required"},
 "bdc2":{"status":"partially_verified","tool_support":[{"tool":"Yanhua ACDP Module 38","functions":["add_key","all_keys_lost","refresh","replacement data copy"],"confidence":"high","source":YANHUA,"limits":"AKL requires separately listed key-learning bench platform."}],"vehicle_applicability":"research_required"}}}
 write(ROOT/"database"/"platforms"/"bmw"/"immobiliser_families.json",data)
 n=add_note("bmw","Official Yanhua material verifies tool support at CAS, FEM, BDC and BDC2 family level. It does not identify which UK chassis carries a family, so model procedures remain research_required.",[YANHUA,YANHUA_FEM]);n+=add_note("mini","BMW Group family evidence is reusable only after the MINI chassis and fitted module are identified; no BMW model mapping is copied.",[YANHUA,YANHUA_FEM]);print(f"BMW/MINI review annotated {n} model families")
def main():
 a=argparse.ArgumentParser();a.add_argument("action",choices=["audit","vag","bmw"]);x=a.parse_args().action;{"audit":audit,"vag":vag,"bmw":bmw}[x]()
if __name__=="__main__":main()
