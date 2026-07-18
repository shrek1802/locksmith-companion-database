#!/usr/bin/env python3
"""Apply exact, catalogue-supported blade profiles without changing other fields."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKED_AT = "2026-07-18"

SILCA_2021 = {
    "publisher": "Silca",
    "title": "Proximity, Slot and Remote Car Keys Catalogue",
    "edition": "05/2021",
    "url": "https://www.lsc.com.au/Documents/SILCA_PROX_SLOT_RKE_05-2021.pdf",
    "checked_at": CHECKED_AT,
    "confidence": "high",
}

SILCA_2025 = {
    "publisher": "Silca",
    "title": "Proximity, Slot and Remote Car Keys Catalogue",
    "edition": "02/2025",
    "url": "https://a.storyblok.com/f/241607/x/72b4b92809/prox-slot-car-key-catalogue-02-2025.pdf",
    "checked_at": CHECKED_AT,
    "confidence": "high",
}

SILCA_TE_2025 = {
    "publisher": "Silca",
    "title": "TE Automotive Keys Catalogue",
    "edition": "2025",
    "url": "https://www.steenhauer.nl/media/20262/file/files2025/catalogo-chiavitevers4.pdf",
    "checked_at": CHECKED_AT,
    "confidence": "high",
}

KEYLINE_2018 = {
    "publisher": "Keyline",
    "title": "POD Keys Vehicle Applications",
    "edition": "2018",
    "url": "https://keyline.it/uploads/file_uploads/upload_en_20180817082853.pdf",
    "checked_at": CHECKED_AT,
    "confidence": "high",
}


# path, profile, status, confidence, evidence sources, catalogue application scope
ASSIGNMENTS = [
    ("alfa_romeo/mito", "SIP22", "verified", "high", [SILCA_2021, SILCA_2025], "Alfa Romeo MiTo (955), 2008-2019"),
    ("alfa_romeo/giulietta", "SIP22", "verified", "high", [SILCA_2021, SILCA_2025], "Alfa Romeo Giulietta (940), 2010-2021"),
    ("chrysler/ypsilon", "SIP22", "verified", "high", [SILCA_2021, SILCA_2025], "Chrysler Ypsilon (312), 2011-2024"),
    ("fiat/500l", "SIP22", "verified", "high", [SILCA_2021, SILCA_2025], "Fiat 500L (351/2), 2012-2022"),
    ("mini/paceman", "HU200", "verified", "high", [SILCA_2021, SILCA_2025], "MINI Paceman (R61), 2012-2016"),
    ("mini/roadster", "HU200", "verified", "high", [SILCA_2021, SILCA_2025], "MINI Roadster (R59), 2011-2015"),
    ("nissan/pulsar", "NSN14", "verified", "high", [SILCA_2021, SILCA_2025], "Nissan Pulsar (C13), from 2014"),
    ("vauxhall/adam", "HU100", "verified", "high", [SILCA_2021, SILCA_2025], "Vauxhall/Opel Adam, 2012-2019"),
    ("opel/adam", "HU100", "verified", "high", [SILCA_2021, SILCA_2025], "Opel Adam, 2012-2019"),
    ("citroen/c3_picasso", "VA2", "verified", "high", [SILCA_2021, SILCA_2025], "Citroen C3 Picasso (A58), 2008-2017"),
    ("peugeot/rcz", "HU83", "verified", "high", [SILCA_TE_2025, KEYLINE_2018], "Peugeot RCZ (T75), 2010-2015"),
    ("renault/modus", "VA2", "verified", "high", [SILCA_2021, SILCA_2025], "Renault Modus (X77), 2004-2012"),
    ("renault/wind", "VA2", "partially_verified", "medium", [SILCA_2021], "Renault Wind, 2010-2012"),
    ("smart/roadster", "YM23", "verified", "high", [SILCA_2021, SILCA_2025], "Smart Roadster (452), 2003-2006"),
    ("suzuki/plash", "HU133R", "verified", "high", [SILCA_2021, SILCA_2025], "Suzuki Splash (EXB), 2008-2015"),
]


def main() -> None:
    changed = 0
    for relative, profile, status, confidence, sources, scope in ASSIGNMENTS:
        path = ROOT / "database" / "vehicles" / relative / "models.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        generations = data.get("generations", [])
        if len(generations) != 1:
            raise ValueError(f"Expected exactly one generation in {path}")

        generation = generations[0]
        existing = generation.get("blade_profile")
        if existing not in (None, "", "unknown", "research_required"):
            raise ValueError(f"Refusing to overwrite blade profile {existing!r} in {path}")

        generation["blade_profile"] = profile
        generation["blade_verification"] = {
            "status": status,
            "confidence": confidence,
            "last_checked": CHECKED_AT,
            "catalogue_application": scope,
            "evidence": [dict(source) for source in sources],
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        changed += 1

    print(f"Updated {changed} blade profiles")


if __name__ == "__main__":
    main()
