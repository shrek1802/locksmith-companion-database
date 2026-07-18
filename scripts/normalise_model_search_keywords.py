#!/usr/bin/env python3
"""Add deterministic, non-technical search terms to UK model manifests."""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VEHICLES = ROOT / "database" / "vehicles"


def ascii_alias(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")


def terms(value: str) -> set[str]:
    variants = {value.strip(), ascii_alias(value).strip(), value.replace("_", " ").strip()}
    for variant in list(variants):
        variants.update(part for part in re.split(r"[^A-Za-z0-9]+", variant) if len(part) > 1)
    return {variant for variant in variants if variant}


def main() -> int:
    changed = 0
    for path in sorted(VEHICLES.glob("*/*/manifest.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        manufacturer = data.get("manufacturer", {})
        model = data.get("model", {})
        keywords: set[str] = {"UK", "RHD"}
        for value in (
            manufacturer.get("id"), manufacturer.get("name"), model.get("id"), model.get("name")
        ):
            if isinstance(value, str):
                keywords.update(terms(value))
        canonical = sorted(keywords, key=lambda item: (item.casefold(), item))
        if data.get("search_keywords") == canonical:
            continue
        data["search_keywords"] = canonical
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        changed += 1
    print(f"model manifests updated: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
