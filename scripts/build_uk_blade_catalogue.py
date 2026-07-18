#!/usr/bin/env python3
"""Build the canonical UK blade-family application catalogue from curated extracts."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


SOURCES = {
    "silca_car_book_4_2014": {
        "publisher": "Silca",
        "title": "The Car Book 4 - Car Keys Guide",
        "edition": "2014",
        "url": "https://automotiveeducation.co.uk/wp-content/uploads/2021/01/The-car-book-and-key-guide.pdf",
        "authority": "primary",
        "checked_at": "2026-07-18",
        "scope": "Vehicle key and blade applications published through 2014",
    },
    "silca_proximity_slot_remote_2025": {
        "publisher": "Silca",
        "title": "Proximity, Slot and Remote Car Keys Catalogue",
        "edition": "02/2025",
        "url": "https://a.storyblok.com/f/241607/x/72b4b92809/prox-slot-car-key-catalogue-02-2025.pdf",
        "authority": "primary",
        "checked_at": "2026-07-18",
        "scope": "Proximity, slot and remote-key blade applications published through February 2025",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--car-book", type=Path, required=True)
    parser.add_argument("--proximity", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    inputs = [
        ("silca_car_book_4_2014", json.loads(args.car_book.read_text(encoding="utf-8"))),
        ("silca_proximity_slot_remote_2025", json.loads(args.proximity.read_text(encoding="utf-8"))),
    ]
    families: dict[str, list[dict]] = defaultdict(list)
    seen: set[tuple] = set()

    for source_id, rows in inputs:
        for row in rows:
            family = row["blade"].upper()
            application = {
                "manufacturer": row["manufacturer"],
                "model": row["model"],
                "model_file": row["path"],
                "generation_or_chassis": row.get("chassis") or "Not specified beyond model and year in catalogue",
                "year_from": row["year_from"],
                "year_to": row.get("year_to"),
                "source_id": source_id,
                "source_page": row.get("page"),
                "catalogue_row": row["raw"],
            }
            identity = (
                family,
                application["manufacturer"],
                application["model"],
                application["generation_or_chassis"],
                application["year_from"],
                application["year_to"],
                source_id,
            )
            if identity not in seen:
                families[family].append(application)
                seen.add(identity)

    items = {}
    for family in sorted(families):
        applications = sorted(
            families[family],
            key=lambda item: (
                item["manufacturer"], item["model"], item["year_from"],
                item["year_to"] or 9999, item["generation_or_chassis"], item["source_id"],
            ),
        )
        items[family.lower()] = {
            "id": family.lower(),
            "display_name": family,
            "status": "catalogue_supported",
            "market_scope": "UK database model set",
            "supported_manufacturers": sorted({item["manufacturer"] for item in applications}),
            "supported_models": sorted({f"{item['manufacturer']}/{item['model']}" for item in applications}),
            "applications": applications,
            "evidence_source_ids": sorted({item["source_id"] for item in applications}),
        }

    output = {
        "schema_version": "2.1",
        "updated_at": "2026-07-18",
        "category": "uk_canonical_blade_applications",
        "market": "UK",
        "drive_side": "RHD",
        "method": (
            "Catalogue applications are filtered to model folders present in the UK database. "
            "A catalogue family is not automatically copied to a vehicle generation unless its full "
            "recorded year range is supported without a conflicting profile."
        ),
        "sources": SOURCES,
        "items": items,
    }
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"families": len(items), "applications": sum(len(v["applications"]) for v in items.values())}))


if __name__ == "__main__":
    main()
