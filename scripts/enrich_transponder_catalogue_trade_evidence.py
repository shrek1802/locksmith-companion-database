#!/usr/bin/env python3
"""Add independently verified UK trade applications to canonical families."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "database/reference/uk_transponder_catalogue.json"

SOURCES = {
    "hickleys_vehicle_keys_2026": {
        "publisher": "Hickleys", "title": "Vehicle Keys, Remotes and Transponders",
        "url": "https://www.hickleys.com/diagnostics/keys_list.php?cat=102", "authority": "secondary_trade",
        "checked_at": "2026-07-18", "discovered_via": "Google search after AI Overview did not finish rendering",
    },
    "nwkeys_pcf7936_id46_2026": {
        "publisher": "NW Keys", "title": "PCF7936 Philips Crypto production chip (46)",
        "url": "https://www.nwkeys.co.uk/Product/pcf7936-philips-crypto-production-chip-46",
        "authority": "secondary_trade", "checked_at": "2026-07-18", "discovered_via": "Google search results",
    },
    "keystation_id46_2026": {
        "publisher": "Keystation", "title": "ID46 T14 PCF7936 Diagnostic Transponder Chip",
        "url": "https://keystation.co.uk/id-46-t14-pcf7936-diagnostics-transponder-chip",
        "authority": "secondary_trade", "checked_at": "2026-07-18", "discovered_via": "Google search results",
    },
    "nwkeys_modern_philips_2026": {
        "publisher": "NW Keys", "title": "Transponder Chips catalogue page 7",
        "url": "https://www.nwkeys.co.uk/Store/transponder-chips?page=7", "authority": "secondary_trade",
        "checked_at": "2026-07-18", "discovered_via": "Google search results",
    },
}

# Exact Hickleys applications whose model folder exists in the UK repository.
ID46_APPLICATIONS = [
    ("vauxhall", "astra", 2004, 2009), ("vauxhall", "zafira", 2005, 2013),
    ("vauxhall", "signum", 2003, 2007), ("vauxhall", "vectra", 2002, 2008),
    ("vauxhall", "corsa", 2007, 2014), ("peugeot", "207", 2006, 2012),
    ("peugeot", "307", 2005, 2008), ("peugeot", "308", 2007, 2008),
    ("citroen", "c4", 2004, 2010), ("citroen", "c6", 2005, 2012),
    ("citroen", "c2", 2005, 2009), ("citroen", "c3", 2006, 2010),
    ("citroen", "c5", 2008, 2011),
]


def model_path(make: str, model: str) -> str:
    return f"database/vehicles/{make}/{model}/models.json"


def main() -> None:
    data = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    data["sources"].update(SOURCES)
    family = data["items"]["philips_crypto2_id46"]
    seen = {(x["model_file"], x["year_from"], x.get("year_to"), x["source_id"]) for x in family["applications"]}
    added = 0
    for make, model, start, end in ID46_APPLICATIONS:
        relative = model_path(make, model)
        if not (ROOT / relative).exists():
            continue
        app = {
            "manufacturer": make, "model": model.replace("_", " "), "model_file": relative,
            "generation_or_chassis": "Exact model/year application published by Hickleys",
            "year_from": start, "year_to": end, "key_variant_scope": "keyed_or_remote_transponder_key",
            "source_id": "hickleys_vehicle_keys_2026", "source_page": None,
            "catalogue_row": f"{make.title()} {model.replace('_', ' ').title()} {start}-{end}: ID46 (PH20 / PCF7941 or PCF7946 as listed)",
        }
        key = (relative, start, end, app["source_id"])
        if key not in seen:
            family["applications"].append(app); seen.add(key); added += 1
    family["applications"].sort(key=lambda x: (x["manufacturer"], x["model"], x["year_from"], x.get("year_to") or 9999, x["source_id"]))
    family["evidence_source_ids"] = sorted(set(family["evidence_source_ids"]) | {"hickleys_vehicle_keys_2026", "nwkeys_pcf7936_id46_2026", "keystation_id46_2026"})
    family["family_verification"] = {
        "status": "verified", "confidence": "high", "last_checked": "2026-07-18",
        "basis": "Silca, Hickleys, NW Keys and Keystation independently identify Philips Crypto ID46/PCF7936; exact vehicle records are upgraded only where separate application ranges overlap.",
        "source_ids": ["silca_car_book_4_2014", "hickleys_vehicle_keys_2026", "nwkeys_pcf7936_id46_2026", "keystation_id46_2026"],
    }
    modern = {
        "silca_id47": "PH/CR3 ID47 / PCF7939FA; NW Keys explicitly lists Ford Transit 2016-2018",
        "silca_id49_1c": "PH/CR3 ID49-1C / PCF7938XA for Honda, Hyundai and Kia",
        "silca_id49_1e": "PH/CR3 ID49-1E / PCF7939MA for Dacia and Renault",
    }
    for family_id, basis in modern.items():
        item = data["items"][family_id]
        item["evidence_source_ids"] = sorted(set(item["evidence_source_ids"]) | {"nwkeys_modern_philips_2026"})
        item["family_verification"] = {"status": "verified", "confidence": "high", "last_checked": "2026-07-18", "basis": basis, "source_ids": ["silca_proximity_slot_remote_2025", "nwkeys_modern_philips_2026"]}
    CATALOGUE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"id46_trade_applications_added": added, "family_statuses_upgraded": 4}))


if __name__ == "__main__":
    main()
