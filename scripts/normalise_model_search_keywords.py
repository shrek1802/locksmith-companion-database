#!/usr/bin/env python3
"""Add deterministic search terms from existing UK vehicle metadata."""

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


SEARCHABLE_METADATA_KEYS = {
    "generation",
    "generation_code",
    "chassis",
    "chassis_code",
    "model_code",
    "platform",
    "platform_code",
}

UNRESOLVED_MARKERS = {
    "confirm",
    "confirmation",
    "exact",
    "research",
    "requires",
    "unknown",
    "unverified",
    "verify",
}


def existing_architecture_terms(node: object) -> set[str]:
    """Return only concise values already asserted by the model record."""
    found: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            if key in SEARCHABLE_METADATA_KEYS and isinstance(value, str):
                clean = " ".join(value.split())
                words = set(re.findall(r"[a-z]+", clean.casefold()))
                if clean and len(clean) <= 60 and not words.intersection(UNRESOLVED_MARKERS):
                    found.update(terms(clean))
            found.update(existing_architecture_terms(value))
    elif isinstance(node, list):
        for value in node:
            found.update(existing_architecture_terms(value))
    return found


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
        model_path = path.with_name("models.json")
        if model_path.exists():
            model_data = json.loads(model_path.read_text(encoding="utf-8"))
            keywords.update(existing_architecture_terms(model_data))
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
