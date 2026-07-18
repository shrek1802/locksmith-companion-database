#!/usr/bin/env python3
"""Build a canonical UK transponder application catalogue from Silca rows.

The input is the model-matched extract produced from Silca Car Book 4.  The
script deliberately retains Silca's published identifier rather than adding
chip technology, bit length, or cloning equivalence not proved by the row.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


SOURCE = {
    "publisher": "Silca",
    "title": "The Car Book 4 - Car Keys Guide",
    "edition": "2014",
    "url": "https://automotiveeducation.co.uk/wp-content/uploads/2021/01/The-car-book-and-key-guide.pdf",
    "authority": "primary",
    "checked_at": "2026-07-18",
    "scope": "Vehicle/transponder applications published through 2014",
}

# Longest/specific expressions first. XX is retained as unresolved evidence,
# never promoted to a concrete family.
TOKEN_RE = re.compile(
    r"\b(PH\s*/\s*CR2\s+46|TEX\s*/\s*CR3\s+6A|TEX\s*/\s*CR2\s+6F|"
    r"TEX\s*/\s*MA\s+6E|(?:PH|TEX|MEG|SOK)\s*/\s*CR\s+[0-9A-Z]+|"
    r"TEXAS\s+4C|PH\s+(?:33|73)|MEG\s+13|TEMIC\s+(?:11|12))\b",
    re.IGNORECASE,
)

REFERENCE_IDS = {
    "TEXAS 4C": "texas_4c",
    "PH 33": "philips_id33",
    "PH/CR 42": "philips_crypto_id42",
    "PH/CR 44": "philips_crypto_id44",
    "PH/CR2 46": "nxp_hitag2_id46",
    "MEG/CR 48": "megamos_crypto_id48",
}


def normalise_token(raw: str) -> tuple[str, str, str] | None:
    matches = list(TOKEN_RE.finditer(raw))
    if not matches:
        return None
    token = re.sub(r"\s+", " ", matches[-1].group(1).upper()).replace(" / ", "/")
    if token == "TEXAS 4C":
        return "texas_fixed_id4c", "Texas fixed ID4C", token
    if token == "MEG 13":
        return "megamos_fixed_id13", "Megamos fixed ID13", token
    if token == "PH 33":
        return "philips_fixed_id33", "Philips fixed ID33", token
    if token == "PH 73":
        return "philips_fixed_id73", "Philips fixed ID73", token
    if token.startswith("TEMIC "):
        code = token.split()[-1]
        return f"temic_fixed_id{code.lower()}", f"Temic fixed ID{code}", token
    prefix, code = token.rsplit(" ", 1)
    if code == "XX":
        return "silca_unspecified_crypto", "Silca crypto type unspecified (XX)", token
    manufacturer = {
        "PH/CR": "Philips crypto", "PH/CR2": "Philips Crypto 2",
        "TEX/CR": "Texas crypto", "TEX/CR2": "Texas Crypto 2",
        "TEX/CR3": "Texas Crypto 3", "TEX/MA": "Texas Megamos application",
        "MEG/CR": "Megamos crypto", "SOK/CR": "Sokymat crypto",
    }[prefix]
    slug = {
        "PH/CR": "philips_crypto", "PH/CR2": "philips_crypto2",
        "TEX/CR": "texas_crypto", "TEX/CR2": "texas_crypto2",
        "TEX/CR3": "texas_crypto3", "TEX/MA": "texas_megamos_application",
        "MEG/CR": "megamos_crypto", "SOK/CR": "sokymat_crypto",
    }[prefix]
    return f"{slug}_id{code.lower()}", f"{manufacturer} ID{code}", token


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--applications", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = json.loads(args.applications.read_text(encoding="utf-8"))
    families: dict[str, list[dict]] = defaultdict(list)
    labels: dict[str, tuple[str, str]] = {}
    seen: set[tuple] = set()
    skipped = 0
    for row in rows:
        parsed = normalise_token(row["raw"])
        if parsed is None:
            skipped += 1
            continue
        family_id, display_name, source_code = parsed
        labels[family_id] = (display_name, source_code)
        app = {
            "manufacturer": row["manufacturer"], "model": row["model"],
            "model_file": row["path"],
            "generation_or_chassis": row.get("chassis") or "Not specified beyond model and year in catalogue",
            "year_from": row["year_from"], "year_to": row.get("year_to"),
            "key_variant_scope": row.get("key_variant_scope", "keyed_or_remote_transponder_key"),
            "source_id": "silca_car_book_4_2014", "source_page": row.get("page"),
            "catalogue_row": row["raw"],
        }
        identity = (family_id, app["manufacturer"], app["model"], app["generation_or_chassis"], app["year_from"], app["year_to"], app["key_variant_scope"])
        if identity not in seen:
            families[family_id].append(app)
            seen.add(identity)
    items = {}
    for family_id in sorted(families):
        apps = sorted(families[family_id], key=lambda x: (x["manufacturer"], x["model"], x["year_from"], x["year_to"] or 9999))
        display, code = labels[family_id]
        concrete = family_id != "silca_unspecified_crypto"
        items[family_id] = {
            "id": family_id, "display_name": display, "silca_code": code,
            "status": "catalogue_supported" if concrete else "research_required",
            "confidence": "high" if concrete else "low",
            "repository_transponder_id": REFERENCE_IDS.get(code, family_id) if concrete else "transponder_unknown",
            "market_scope": "UK database model set",
            "supported_manufacturers": sorted({x["manufacturer"] for x in apps}),
            "supported_models": sorted({f'{x["manufacturer"]}/{x["model"]}' for x in apps}),
            "applications": apps, "evidence_source_ids": ["silca_car_book_4_2014"],
        }
    out = {
        "schema_version": "2.1", "updated_at": "2026-07-18",
        "category": "uk_canonical_transponder_applications", "market": "UK", "drive_side": "RHD",
        "method": "Canonical families preserve the exact Silca transponder identifier. Applications are filtered to models present in the UK database; model records are updated only when their full year range and key scope are supported without conflict.",
        "sources": {"silca_car_book_4_2014": SOURCE}, "items": items,
        "build_summary": {"input_rows": len(rows), "matched_rows": sum(len(x) for x in families.values()), "rows_without_published_transponder": skipped},
    }
    args.output.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"families": len(items), "applications": sum(len(x["applications"]) for x in items.values()), "skipped": skipped}))


if __name__ == "__main__":
    main()
