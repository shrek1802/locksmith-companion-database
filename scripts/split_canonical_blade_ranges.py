#!/usr/bin/env python3
"""Split broad generation records into catalogue-supported blade/key scopes."""

from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOGUE_PATH = ROOT / "database/reference/uk_blade_catalogue.json"
SUPPORTED_SCOPES = {
    "keyed_or_remote_transponder_key": "keyed_or_remote",
    "remote_or_flip_key": "remote_or_flip",
    "proximity_emergency_insert": "proximity",
    "slot_key": "slot_key",
}


def parse_years(value):
    years = [int(year) for year in re.findall(r"(?:19|20)\d{2}", value or "")]
    if not years:
        return None
    end = years[1] if len(years) > 1 else (2026 if re.search(r"present|current", value or "", re.I) else years[0])
    return years[0], end


def app_end(application):
    if isinstance(application.get("year_to"), int):
        return application["year_to"]
    return 2025 if application["source_id"] == "silca_proximity_slot_remote_2025" else 2014


def year_text(start, end):
    return f"{start}-present" if end == 2026 else f"{start}-{end}"


def slug(value):
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def segments(values):
    output=[]
    for year, state in values:
        if not output or output[-1][2] != state:
            output.append([year, year, state])
        else:
            output[-1][1] = year
    return output


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--manufacturers", help="Comma-separated database manufacturer folder IDs")
    args=parser.parse_args()
    manufacturer_filter={item.strip() for item in (args.manufacturers or "").split(",") if item.strip()}
    catalogue=json.loads(CATALOGUE_PATH.read_text(encoding="utf-8"))
    apps_by_file=defaultdict(list)
    for family_id,family in catalogue["items"].items():
        for app in family["applications"]:
            if app.get("key_variant_scope") in SUPPORTED_SCOPES:
                apps_by_file[app["model_file"]].append((family_id,app))

    changed_files=[]; created=[]; resolved=Counter(); boundary_records=0
    for relative,applications in sorted(apps_by_file.items()):
        manufacturer=Path(relative).parts[2] if len(Path(relative).parts)>2 else ""
        if manufacturer_filter and manufacturer not in manufacturer_filter:
            continue
        path=ROOT/relative
        data=json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data.get("generations"),list):
            continue
        replacement=[]; file_changed=False
        for generation in data["generations"]:
            if generation.get("catalogue_split"):
                replacement.append(generation); continue
            verification=generation.get("blade_verification",{})
            if isinstance(verification,dict) and verification.get("canonical_blade_family_id"):
                replacement.append(generation); continue
            year_range=parse_years(generation.get("years"))
            if not year_range:
                replacement.append(generation); continue
            start,end=year_range
            overlapping=[(family,app) for family,app in applications if app["year_from"]<=end and app_end(app)>=start]
            if not overlapping:
                replacement.append(generation); continue

            scoped_segments=[]
            for scope,variant_type in SUPPORTED_SCOPES.items():
                scope_apps=[(family,app) for family,app in overlapping if app["key_variant_scope"]==scope]
                if not scope_apps: continue
                timeline=[]
                for year in range(start,end+1):
                    families=tuple(sorted({family for family,app in scope_apps if app["year_from"]<=year<=app_end(app)}))
                    timeline.append((year,families))
                for seg_start,seg_end,families in segments(timeline):
                    if families:
                        scoped_segments.append((scope,variant_type,seg_start,seg_end,families,scope_apps))
            if not scoped_segments:
                replacement.append(generation); continue

            file_changed=True
            covered_years=set()
            origin_id=generation.get("id") or slug(generation.get("name","generation"))
            for scope,variant_type,seg_start,seg_end,families,scope_apps in scoped_segments:
                covered_years.update(range(seg_start,seg_end+1))
                clone=copy.deepcopy(generation)
                family_label="_or_".join(families)
                clone["id"]=f"{origin_id}_{seg_start}_{seg_end}_{slug(scope)}_{family_label}"
                clone["name"]=f"{generation.get('name',origin_id)} - {variant_type} ({year_text(seg_start,seg_end)})"
                clone["years"]=year_text(seg_start,seg_end)
                clone["key_variants"]=[{"type":variant_type,"status":"partially_verified" if len(families)==1 else "research_required"}]
                evidence_apps=[app for family,app in scope_apps if family in families and app["year_from"]<=seg_end and app_end(app)>=seg_start]
                clone["catalogue_split"]={
                    "origin_generation_id":origin_id,
                    "key_variant_scope":scope,
                    "boundary_basis":"Silca catalogue application year range",
                    "last_checked":"2026-07-18",
                    "source_rows":[app["catalogue_row"] for app in evidence_apps],
                }
                if len(families)==1:
                    family_id=families[0]; family=catalogue["items"][family_id]
                    source_ids=sorted({app["source_id"] for app in evidence_apps})
                    clone["blade_profile"]=family["display_name"]
                    clone["blade_id"]=family_id
                    clone["blade_verification"]={
                        "status":"verified" if len(source_ids)>1 else "partially_verified",
                        "confidence":"high" if len(source_ids)>1 else "medium",
                        "last_checked":"2026-07-18",
                        "canonical_blade_family_id":family_id,
                        "record_year_range":year_text(seg_start,seg_end),
                        "key_variant_scope":scope,
                        "evidence":[{
                            "source_id":source_id,
                            "publisher":catalogue["sources"][source_id]["publisher"],
                            "title":catalogue["sources"][source_id]["title"],
                            "edition":catalogue["sources"][source_id]["edition"],
                            "url":catalogue["sources"][source_id]["url"],
                            "catalogue_rows":[app["catalogue_row"] for app in evidence_apps if app["source_id"]==source_id],
                        } for source_id in source_ids],
                    }
                    resolved[family_id]+=1
                else:
                    clone["blade_profile"]="research_required"
                    clone["blade_id"]="emergency_blade_unknown" if scope=="proximity_emergency_insert" else None
                    clone["blade_transition_candidates"]=list(families)
                    clone["blade_verification"]={
                        "status":"research_required","confidence":"conflicting_catalogue_applications",
                        "last_checked":"2026-07-18","record_year_range":year_text(seg_start,seg_end),
                        "key_variant_scope":scope,
                    }
                    boundary_records+=1
                replacement.append(clone)
                created.append({"file":relative,"record_id":clone["id"],"families":list(families),"years":clone["years"],"scope":scope})

            uncovered=[(year,year not in covered_years) for year in range(start,end+1)]
            for gap_start,gap_end,is_gap in segments(uncovered):
                if not is_gap: continue
                clone=copy.deepcopy(generation)
                clone["id"]=f"{origin_id}_{gap_start}_{gap_end}_blade_research"
                clone["name"]=f"{generation.get('name',origin_id)} - blade research boundary ({year_text(gap_start,gap_end)})"
                clone["years"]=year_text(gap_start,gap_end)
                clone["blade_profile"]="research_required"
                clone["blade_id"]=None
                clone["blade_verification"]={
                    "status":"research_required","confidence":"catalogue_year_range_not_covered",
                    "last_checked":"2026-07-18","record_year_range":year_text(gap_start,gap_end),
                }
                clone["catalogue_split"]={
                    "origin_generation_id":origin_id,"key_variant_scope":"unresolved",
                    "boundary_basis":"Outside current canonical catalogue coverage","last_checked":"2026-07-18",
                }
                replacement.append(clone); boundary_records+=1
                created.append({"file":relative,"record_id":clone["id"],"families":[],"years":clone["years"],"scope":"unresolved"})
        if file_changed:
            data["generations"]=replacement
            changed_files.append(relative)
            if args.apply:
                path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"apply":args.apply,"changed_files":changed_files,"created_records":created,"resolved_families":dict(resolved),"boundary_records":boundary_records},indent=2))


if __name__=="__main__": main()
