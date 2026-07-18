#!/usr/bin/env python3
"""Create conservative UK/RHD Audi transverse-platform model records."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDI = ROOT / "database" / "vehicles" / "audi"

MODELS = {
    "a3": {
        "name": "A3",
        "generations": [
            ("8l", "A3 8L", "1996-2003", "PQ34"),
            ("8p", "A3 8P", "2003-2013", "PQ35"),
            ("8v", "A3 8V", "2012-2020", "MQB"),
            ("8y", "A3 8Y", "2020-present", "MQB Evo"),
        ],
    },
    "q2": {"name": "Q2", "generations": [("ga", "Q2 GA", "2016-present", "MQB")]},
    "q3": {
        "name": "Q3",
        "generations": [
            ("8u", "Q3 8U", "2011-2018", "PQ35 derivative"),
            ("f3", "Q3 F3", "2018-2025", "MQB"),
            ("f3_2025", "Q3 from 2025", "2025-present", "platform requires technical confirmation"),
        ],
    },
    "tt": {
        "name": "TT",
        "generations": [
            ("8n", "TT 8N", "1998-2006", "PQ34"),
            ("8j", "TT 8J", "2006-2014", "second-generation A3 platform"),
            ("8s", "TT 8S", "2014-2023", "MQB"),
        ],
    },
}

AUDI_ARCHIVE = {
    "publisher": "Audi UK Newsroom",
    "title": "Audi UK current, previous and heritage model archive",
    "url": "https://press.audi.co.uk/models/concept/releases",
    "supports": ["UK model presence and broad production-era context"],
}


def write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def create_model(model_id: str, spec: dict) -> None:
    model_dir = AUDI / model_id
    name = spec["name"]
    write(model_dir / "manifest.json", {
        "schema_version": "2.1", "updated_at": "2026-07-18",
        "manufacturer": {"id": "audi", "name": "Audi"},
        "model": {"id": model_id, "name": name}, "version": 1,
        "files": {key: f"{key}.json" for key in ("models", "procedures", "modules", "wiring", "service_functions", "notes", "photos")},
        "verification": {"status": "research_in_progress", "market": "UK", "drive_side": "RHD"},
    })
    generations = []
    for gen_id, gen_name, years, platform in spec["generations"]:
        generations.append({
            "id": gen_id, "name": gen_name, "years": years, "platform": platform,
            "immobiliser_family": "Exact family requires generation and fitted-hardware evidence",
            "key_variants": [
                {"type": "keyed", "status": "research_required"},
                {"type": "advanced_key_or_keyless", "status": "research_required"},
            ],
            "status": "research_in_progress",
        })
    write(model_dir / "models.json", {
        "schema_version": "2.1", "model": name, "market": "UK", "drive_side": "RHD",
        "generations": generations, "sources": {"audi_uk_model_archive": AUDI_ARCHIVE},
    })
    write(model_dir / "procedures.json", {
        "schema_version": "2.1", "model": name,
        "procedures": [
            {"id": "add_key", "name": "Add key", "method": "No model-wide route; identify generation, dashboard and key system", "status": "research_in_progress"},
            {"id": "akl", "name": "All keys lost", "method": "No model-wide route verified", "status": "research_in_progress"},
        ],
    })
    write(model_dir / "modules.json", {
        "schema_version": "2.1", "model": name,
        "modules": [
            {"id": "instrument_cluster", "name": "Instrument cluster", "role": "Generation dependent", "location": "UK RHD location not verified", "status": "research_in_progress"},
            {"id": "bcm_or_access_start", "name": "BCM/access-start system", "role": "Generation and key-system dependent", "location": "UK RHD location not verified", "status": "research_in_progress"},
            {"id": "gateway", "name": "Gateway", "role": "Diagnostic/security role not verified", "location": "UK RHD location not verified", "status": "research_in_progress"},
        ],
    })
    write(model_dir / "wiring.json", {
        "schema_version": "2.1", "model": name,
        "connections": [
            {"id": "obd", "name": "OBD-II connector", "location": "UK RHD location not verified", "status": "research_in_progress"},
            {"id": "bench", "name": "Bench connection", "notes": "No wiring, EEPROM, MCU or adapter claim without exact hardware evidence.", "status": "research_in_progress"},
        ],
    })
    write(model_dir / "service_functions.json", {
        "schema_version": "2.1", "model": name,
        "functions": [
            {"id": "key_count", "name": "Read learned key count", "availability": "Generation/tool dependent", "status": "research_in_progress"},
            {"id": "remote_sync", "name": "Remote synchronisation", "availability": "Key-system dependent", "status": "research_in_progress"},
        ],
    })
    write(model_dir / "notes.json", {
        "schema_version": "2.1", "model": name,
        "notes": [
            {"title": "Evidence boundary", "text": "Audi UK evidence supports UK model presence. Platform labels are architecture context and do not verify locksmith procedures."},
            {"title": "Reuse audit", "text": "No repository claim met the two-source record-level threshold for automatic inheritance."},
            {"title": "Variant policy", "text": "Keyed and advanced-key/keyless variants must be verified separately by generation and fitted hardware."},
        ], "status": "research_in_progress",
    })
    write(model_dir / "photos.json", {
        "schema_version": "2.1", "model": name, "photos": [],
        "required": ["UK RHD OBD location", "Module locations", "Key and blade examples"],
        "status": "awaiting_verified_images",
    })


def main() -> int:
    for model_id, spec in MODELS.items():
        create_model(model_id, spec)
    manifest_path = AUDI / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["updated_at"] = "2026-07-18"
    manifest["version"] = 2
    for model_id, spec in MODELS.items():
        manifest["models"][model_id] = {"name": spec["name"], "version": 1, "manifest": f"{model_id}/manifest.json", "status": "research_in_progress"}
    write(manifest_path, manifest)
    for root_manifest in (ROOT / "manifest.json", ROOT / "database" / "manifest.json"):
        data = json.loads(root_manifest.read_text(encoding="utf-8"))
        data["manufacturers"]["audi"].update({"version": 2, "updated_at": "2026-07-18"})
        write(root_manifest, data)
    print("created Audi transverse batch: A3, Q2, Q3, TT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
