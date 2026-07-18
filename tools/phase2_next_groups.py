#!/usr/bin/env python3
"""Evidence-bounded Phase-2 reviews for four shared architecture groups."""
from __future__ import annotations
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TODAY="2026-07-18"
GBOX="https://www.autel.com/u/cms/www/202406/05060914c599.pdf"
FDRS="https://www.motorcraftservice.com/Diagnostic/HelmSupport?categoryId=276&channelId=50&country=USA&language=EN-US"
AD_FIAT="https://www.advanced-diagnostics.com/news-posts/software-update-compatible-with-fiat-01-2026-ads2327"
AD_RENAULT="https://www.advanced-diagnostics.com/news-posts/software-update-compatible-with-renault-10-2025-ads2325"
AD_CABLE="https://www.advanced-diagnostics.com/smart-pro-accessories/renault-bypass-cable-adc2017"
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def annotate(makes,families,sources,scope):
 n=0
 for make in makes:
  for p in (ROOT/"database"/"vehicles"/make).glob("*/models.json"):
   d=json.loads(p.read_text(encoding="utf-8"))
   d["phase2_architecture_review"]={"checked_at":TODAY,"families_reviewed":families,"status":"partially_verified at named family/tool scope; model applicability remains research_required","scope_limit":scope,"sources":sources,"confidence":"high for official vendor/OEM claims"};write(p,d);n+=1
 return n
def mercedes():
 makes=["mercedes_benz","smart"]
 data={"schema_version":"1.0","updated_at":TODAY,"manufacturer_group":["Mercedes-Benz","Smart"],"families":{
 "das3_eis_ezs":{"status":"partially_verified","architecture":"DAS3 CAN EIS/EZS family","tool_support":[{"tool":"Autel MaxiIM with G-BOX3","operation":"All keys lost password calculation/programming assistance","methods":["on_vehicle","bench"],"confidence":"high","source":GBOX}],"limits":"The source does not establish every vehicle/EIS, FBS generation, RHD location or wiring."},
 "fbs3":{"status":"research_required","notes":"Do not equate every DAS3 vendor menu with every FBS3 vehicle."},"fbs4":{"status":"research_required","notes":"No offline capability inferred; authorised restrictions remain model/operation specific."},"keyless_go":{"status":"research_required"},"smart_legacy":{"status":"research_required","notes":"Smart SAM/immobiliser systems are not inherited from Mercedes passenger-car EIS/EZS."}}}
 write(ROOT/"database"/"platforms"/"mercedes_benz"/"immobiliser_families.json",data)
 n=annotate(makes,list(data["families"]),[GBOX],"DAS3 tool capability only; no FBS4, model, keyless, online, location or wiring inheritance")
 print(f"Mercedes-Benz/Smart reviewed {n} model records")
def ford():
 data={"schema_version":"1.0","updated_at":TODAY,"manufacturer_group":["Ford"],"quarantine_policy":"reports/ford_modern_safety_quarantine.json and scripts/audit_ford_security_access.py remain authoritative","families":{
 "legacy_pats":{"status":"partially_verified","variants":["keyed","proximity"],"limits":"Exact transponder, module and security access remain record-specific."},
 "bcm_ipc_pats":{"status":"partially_verified","limits":"BCM versus IPC role must follow the stored generation record."},"rfa_kvm_proximity":{"status":"research_required"},
 "fdrs_restricted":{"status":"verified_source","architecture":"Ford cloud-based next-generation diagnostic system for some 2018-forward vehicles","source":FDRS,"confidence":"high","limits":"Does not prove a key-programming function or online requirement for every model."},"commercial_variants":{"status":"research_required"}}}
 write(ROOT/"database"/"platforms"/"ford"/"immobiliser_families.json",data)
 n=annotate(["ford"],list(data["families"]),[FDRS,"reports/ford_modern_safety_quarantine.json"],"Preserve per-record security classification; no quarantined route promoted")
 print(f"Ford reviewed {n} model records; quarantine preserved")
def stellantis():
 makes=["peugeot","citroen","ds","vauxhall","opel","fiat","abarth","alfa_romeo","jeep","chrysler"]
 data={"schema_version":"1.0","updated_at":TODAY,"manufacturer_group":["PSA","FCA","Stellantis"],"families":{
 "psa_bsi_keyed":{"status":"research_required"},"psa_bsi_proximity":{"status":"research_required"},"legacy_gm_opel":{"status":"research_required"},"fiat_code_bcm":{"status":"research_required"},
 "fca_sgw":{"status":"partially_verified","notes":"SGW/bypass applicability is vehicle and tool specific; no universal 12+8 claim."},
 "stellantis_large_van":{"status":"partially_verified","tool_support":[{"tool":"Advanced Diagnostics Smart Pro ADS2327","models":["Fiat Ducato","Peugeot Boxer","Opel Movano"],"operation":"Programs remote and transponder; erases existing keys first; no working key required","confidence":"high","source":AD_FIAT}],"limits":"Iveco-specific ADC2026 requirement is not copied to the three Stellantis vans."}}}
 write(ROOT/"database"/"platforms"/"stellantis"/"immobiliser_families.json",data)
 n=annotate(makes,list(data["families"]),[AD_FIAT],"PSA BSI and FCA BCM/SGW remain separate; no model mapping except explicitly named commercial vans")
 # Promote only the vendor-named models' general AKL/add-key evidence.
 upgraded=0
 for make,model in (("fiat","ducato"),("peugeot","boxer"),("opel","movano")):
  p=ROOT/"database"/"vehicles"/make/model/"procedures.json";d=json.loads(p.read_text(encoding="utf-8"))
  for item in d.get("procedures",[]):
   if item.get("id") in {"add_key_keyed","akl_keyed"} and item.get("status")=="research_required":item["status"]="partially_verified";item["evidence"]={"tool":"Smart Pro ADS2327","source":AD_FIAT,"confidence":"high","limits":"Exact generation and key hardware require confirmation"};upgraded+=1
  write(p,d)
 print(f"Stellantis reviewed {n} model records and upgraded {upgraded} named-van procedure statuses")
def renault():
 makes=["renault","dacia","nissan"]
 data={"schema_version":"1.0","updated_at":TODAY,"manufacturer_group":["Renault","Dacia","Nissan"],"families":{
 "renault_uch_keyed":{"status":"research_required"},"renault_card_slot":{"status":"research_required"},"renault_proximity":{"status":"partially_verified","tool_support":[{"tool":"Smart Pro ADS2325 with ADC2017","models":["Renault Clio","Renault Captur","Renault Zoe"],"operation":"duplicate/program proximity keys","confidence":"high","source":AD_CABLE}]},
 "alliance_bcm_bypass":{"status":"partially_verified","tool_support":[{"tool":"Smart Pro ADS2325","scope":"extended Renault and Nissan range; bladed and proximity keys; many AKL","confidence":"high","source":AD_RENAULT}],"limits":"Exact model coverage and 16+32 versus 40-pin cable must be confirmed."},"nissan_nats_keyed":{"status":"research_required"},"nissan_i_key":{"status":"research_required"}}}
 write(ROOT/"database"/"platforms"/"renault_nissan"/"immobiliser_families.json",data)
 n=annotate(makes,list(data["families"]),[AD_RENAULT,AD_CABLE],"UCH and Nissan BCM/NATS are not merged solely because a vendor shares a bypass family")
 upgraded=0
 for model in ("clio","captur","zoe"):
  p=ROOT/"database"/"vehicles"/"renault"/model/"procedures.json";d=json.loads(p.read_text(encoding="utf-8"))
  for item in d.get("procedures",[]):
   if item.get("id")=="add_key_proximity" and item.get("status")=="research_required":item["status"]="partially_verified";item["evidence"]={"tool":"Smart Pro ADS2325 with ADC2017","source":AD_CABLE,"confidence":"high","limits":"Exact generation/build and key hardware require confirmation"};upgraded+=1
  write(p,d)
 print(f"Renault/Dacia/Nissan reviewed {n} model records and upgraded {upgraded} proximity statuses")
def main():
 a=argparse.ArgumentParser();a.add_argument("action",choices=["mercedes","ford","stellantis","renault"]);{"mercedes":mercedes,"ford":ford,"stellantis":stellantis,"renault":renault}[a.parse_args().action]()
if __name__=="__main__":main()
