#!/usr/bin/env python3
"""Rebuild the raw-file database update metadata consumed by the mobile app."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VEHICLES = ROOT / "database" / "vehicles"
REFERENCE = ROOT / "database" / "reference"
TODAY = "2026-07-19"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def save_compact(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def next_version(value: Any) -> int:
    try:
        return int(value) + 1
    except (TypeError, ValueError):
        return 1


def record_count(models_path: Path) -> int:
    data = load(models_path)
    if isinstance(data.get("records"), list):
        return len(data["records"])
    if isinstance(data.get("items"), dict):
        return len(data["items"])
    if isinstance(data.get("generations"), list):
        return len(data["generations"])
    return 0


def rebuild(version: str, source_commit: str) -> None:
    root_manifest_path = ROOT / "manifest.json"
    root_manifest = load(root_manifest_path)
    manufacturers = root_manifest.get("manufacturers", {})
    model_total = 0
    record_total = 0

    for manufacturer_id, root_entry in sorted(manufacturers.items()):
        manufacturer_manifest_path = VEHICLES / manufacturer_id / "manifest.json"
        manufacturer_manifest = load(manufacturer_manifest_path)
        model_entries = manufacturer_manifest.get("models", {})

        for models_path in sorted((VEHICLES / manufacturer_id).glob("*/models.json")):
            model_id = models_path.parent.name
            if model_id in model_entries:
                continue
            models_data = load(models_path)
            model_name = models_data.get("model")
            if not isinstance(model_name, str) or not model_name.strip():
                candidates = list(models_data.get("items", {}).values()) + models_data.get("records", [])
                first = candidates[0] if candidates else {}
                vehicle = first.get("vehicle", first.get("vehicle_information", {}))
                model_name = vehicle.get("model", model_id.replace("_", " ").title())
            model_manifest_path = models_path.parent / "manifest.json"
            if not model_manifest_path.exists():
                save(model_manifest_path, {
                    "schema_version": "2.2",
                    "updated_at": TODAY,
                    "manufacturer": {"id": manufacturer_id, "name": manufacturer_manifest["manufacturer"]["name"]},
                    "model": {"id": model_id, "name": model_name},
                    "version": 0,
                    "files": {"models": "models.json"},
                    "verification": {"market": "UK", "drive_side": "RHD"},
                })
            model_entries[model_id] = {
                "name": model_name,
                "version": 0,
                "manifest": f"{model_id}/manifest.json",
                "status": "research_in_progress",
            }

        for model_id, model_entry in sorted(model_entries.items()):
            model_manifest_path = VEHICLES / manufacturer_id / model_id / "manifest.json"
            model_manifest = load(model_manifest_path)
            model_manifest["version"] = next_version(model_manifest.get("version"))
            model_manifest["updated_at"] = TODAY

            checksums: dict[str, str] = {}
            for component_id, component_reference in model_manifest.get("files", {}).items():
                relative_file = component_reference if isinstance(component_reference, str) else component_reference.get("file")
                component_path = model_manifest_path.parent / relative_file
                checksums[component_id] = sha256(component_path)
                if component_id in {"models", "vehicles"}:
                    record_total += record_count(component_path)
            model_manifest["checksums"] = checksums
            save(model_manifest_path, model_manifest)

            model_entry["version"] = model_manifest["version"]
            model_entry["sha256"] = sha256(model_manifest_path)
            model_total += 1

        manufacturer_manifest["version"] = next_version(manufacturer_manifest.get("version"))
        manufacturer_manifest["updated_at"] = TODAY
        save(manufacturer_manifest_path, manufacturer_manifest)

        root_entry["version"] = manufacturer_manifest["version"]
        root_entry["updated_at"] = TODAY
        root_entry["sha256"] = sha256(manufacturer_manifest_path)

    reference_manifest_path = REFERENCE / "manifest.json"
    reference_manifest = load(reference_manifest_path)
    reference_manifest["updated_at"] = TODAY
    reference_manifest["version"] = next_version(reference_manifest.get("version"))
    reference_manifest.setdefault("files", {}).update({
        "uk_chip_catalogue": "uk_chip_catalogue.json",
        "key_profile_schema": "key_profile_schema.json",
    })
    reference_manifest["checksums"] = {
        key: sha256(REFERENCE / (value if isinstance(value, str) else value["file"]))
        for key, value in sorted(reference_manifest["files"].items())
    }
    save(reference_manifest_path, reference_manifest)

    root_manifest.update({
        "schema_version": "2.2",
        "updated_at": TODAY,
        "database_version": version,
        "source_commit": source_commit,
        "reference_manifest": "database/reference/manifest.json",
        "package_index": "database/update_manifest.json",
    })
    update_manifest_path = ROOT / "database" / "update_manifest.json"
    database_package_path = ROOT / "database" / "database-update.json"
    database_manifest_path = ROOT / "database" / "manifest.json"
    package_source_paths = [
        path for path in sorted((ROOT / "database").rglob("*.json"))
        if path not in {update_manifest_path, database_package_path, database_manifest_path}
    ]
    database_package = {
        "schema_version": "2.2",
        "database_version": version,
        "generated_at": TODAY,
        "source_commit": source_commit,
        "counts": {
            "manufacturers": len(manufacturers),
            "models": model_total,
            "vehicle_records": record_total,
            "json_files": len(package_source_paths),
        },
        "display_contract": {
            "file": "database/reference/key_profile_schema.json",
            "order": ["blade_profile", "transponder_id", "technology_family", "chip_type", "chip_ic", "remote_configuration", "frequency"],
        },
        "canonical_catalogues": {
            "blade": "database/reference/uk_blade_catalogue.json",
            "transponder": "database/reference/uk_transponder_catalogue.json",
            "chip": "database/reference/uk_chip_catalogue.json",
        },
        "files": {
            path.relative_to(ROOT).as_posix(): load(path)
            for path in package_source_paths
        },
    }
    save_compact(database_package_path, database_package)
    package_sha256 = sha256(database_package_path)
    package_size = database_package_path.stat().st_size
    package_url = "database/database-update.json"
    root_manifest.update({
        "package_url": package_url,
        "package_sha256": package_sha256,
        "package_size": package_size,
        "package_format": "indexed_json",
        "package_counts": database_package["counts"],
    })
    save(root_manifest_path, root_manifest)
    save(database_manifest_path, root_manifest)

    indexed_paths = [root_manifest_path]
    indexed_paths.extend(sorted((ROOT / "database").rglob("*.json")))
    indexed_paths = [path for path in indexed_paths if path != update_manifest_path]
    files = {
        path.relative_to(ROOT).as_posix(): {
            "sha256": sha256(path),
            "size": path.stat().st_size,
        }
        for path in indexed_paths
    }
    package = {
        "schema_version": "2.2",
        "database_version": version,
        "generated_at": TODAY,
        "source_commit": source_commit,
        "delivery": {
            "type": "single_indexed_json",
            "root_manifest": "manifest.json",
            "base_url": "https://raw.githubusercontent.com/shrek1802/locksmith-companion-database/main/",
            "package_url": package_url,
            "package_sha256": package_sha256,
            "package_size": package_size,
            "package_format": "indexed_json",
        },
        "display_contract": {
            "file": "database/reference/key_profile_schema.json",
            "order": ["blade_profile", "transponder_id", "technology_family", "chip_type", "chip_ic", "remote_configuration", "frequency"],
        },
        "canonical_catalogues": {
            "blade": "database/reference/uk_blade_catalogue.json",
            "transponder": "database/reference/uk_transponder_catalogue.json",
            "chip": "database/reference/uk_chip_catalogue.json",
        },
        "counts": {
            "manufacturers": len(manufacturers),
            "models": model_total,
            "vehicle_records": record_total,
            "json_files": len(package_source_paths),
        },
        "files": files,
    }
    package_bytes = (json.dumps(package, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    package["package_checksum"] = hashlib.sha256(package_bytes).hexdigest()
    save(update_manifest_path, package)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--source-commit", required=True)
    args = parser.parse_args()
    rebuild(args.version, args.source_commit)


if __name__ == "__main__":
    main()
