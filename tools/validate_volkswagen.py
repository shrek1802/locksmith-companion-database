#!/usr/bin/env python3
"""Validate Volkswagen database structure and core schema consistency.

This validator is intentionally conservative: it checks structure, references,
UK/RHD scope, procedure readability and approved status vocabulary without
attempting to prove technical vehicle claims.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VW_ROOT = ROOT / "database" / "vehicles" / "volkswagen"
VW_MANIFEST = VW_ROOT / "manifest.json"
ROOT_MANIFESTS = [ROOT / "manifest.json", ROOT / "database" / "manifest.json"]
REQUIRED_FILES = {
    "manifest.json",
    "models.json",
    "procedures.json",
    "modules.json",
    "wiring.json",
    "service_functions.json",
    "notes.json",
    "photos.json",
}
APPROVED_STATUS = {
    "supported",
    "conditional",
    "verification_required",
    "research_required",
    "not_supported",
    "research_in_progress",
    "to_be_verified",
    "fully_verified",
    # Existing document-level lifecycle values retained until the Volkswagen
    # procedure files are migrated to a dedicated document_status field.
    "operation_specific_tool_support_added_with_conditions",
    "operation_specific_tool_support_partially_verified",
}
RAW_PROCEDURE_PREFIX = "PROC_"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON: {path.relative_to(ROOT)} line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def walk_values(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def normalise_status(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def validate() -> list[str]:
    errors: list[str] = []

    try:
        manufacturer = load_json(VW_MANIFEST)
    except ValueError as exc:
        return [str(exc)]

    if manufacturer.get("schema_version") != "2.1":
        errors.append("Volkswagen manifest schema_version must be 2.1")

    maker = manufacturer.get("manufacturer", {})
    if maker.get("market") != "UK" or maker.get("drive_side") != "RHD":
        errors.append("Volkswagen manifest must declare UK market and RHD drive side")

    models = manufacturer.get("models")
    if not isinstance(models, dict) or not models:
        errors.append("Volkswagen manifest contains no model map")
        return errors

    manufacturer_version = manufacturer.get("version")
    for root_manifest_path in ROOT_MANIFESTS:
        try:
            root_manifest = load_json(root_manifest_path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        vw_entry = root_manifest.get("manufacturers", {}).get("volkswagen", {})
        if vw_entry.get("version") != manufacturer_version:
            errors.append(
                f"Version mismatch: {root_manifest_path.relative_to(ROOT)} records Volkswagen "
                f"version {vw_entry.get('version')!r}, expected {manufacturer_version!r}"
            )

    for model_id, entry in sorted(models.items()):
        model_dir = VW_ROOT / model_id
        rel_dir = model_dir.relative_to(ROOT)
        if not model_dir.is_dir():
            errors.append(f"Missing model directory: {rel_dir}")
            continue

        present = {path.name for path in model_dir.iterdir() if path.is_file()}
        for missing in sorted(REQUIRED_FILES - present):
            errors.append(f"{rel_dir}: missing {missing}")

        manifest_path = model_dir / "manifest.json"
        try:
            model_manifest = load_json(manifest_path)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        declared_model = model_manifest.get("model", {})
        if declared_model.get("id") != model_id:
            errors.append(f"{rel_dir}/manifest.json: model.id does not match directory name")

        if model_manifest.get("version") != entry.get("version"):
            errors.append(
                f"{rel_dir}/manifest.json: version {model_manifest.get('version')!r} does not "
                f"match manufacturer manifest {entry.get('version')!r}"
            )

        files = model_manifest.get("files", {})
        expected_refs = {
            "models": "models.json",
            "procedures": "procedures.json",
            "modules": "modules.json",
            "wiring": "wiring.json",
            "service_functions": "service_functions.json",
            "notes": "notes.json",
            "photos": "photos.json",
        }
        for key, filename in expected_refs.items():
            if files.get(key) != filename:
                errors.append(f"{rel_dir}/manifest.json: files.{key} must reference {filename}")

        try:
            models_data = load_json(model_dir / "models.json")
            procedures_data = load_json(model_dir / "procedures.json")
        except ValueError as exc:
            errors.append(str(exc))
            continue

        for key, value in walk_values(models_data):
            if key == "market" and value != "UK":
                errors.append(f"{rel_dir}/models.json: non-UK market value {value!r}")
            if key == "drive_side" and value != "RHD":
                errors.append(f"{rel_dir}/models.json: non-RHD drive_side value {value!r}")

        procedure_items = procedures_data.get("items")
        if procedure_items is None:
            # A small number of established Volkswagen files still use the
            # older top-level name. Validate their records while they are
            # migrated rather than hiding all of their other data-quality errors.
            procedure_items = procedures_data.get("procedures")
        if procedure_items is None:
            errors.append(
                f"{rel_dir}/procedures.json: missing top-level 'items' procedure records"
            )
            procedure_items = {}

        for key, value in walk_values(procedures_data):
            if isinstance(value, str) and value.startswith(RAW_PROCEDURE_PREFIX):
                errors.append(f"{rel_dir}/procedures.json: raw procedure ID remains: {value}")
            if key in {"status", "overall_status", "tool_support"} and isinstance(value, str):
                status = normalise_status(value)
                if status not in APPROVED_STATUS:
                    errors.append(
                        f"{rel_dir}/procedures.json: unapproved status value {value!r}"
                    )

        if isinstance(procedure_items, dict):
            for generation_id, operations in procedure_items.items():
                if not isinstance(operations, dict):
                    errors.append(
                        f"{rel_dir}/procedures.json: {generation_id} must be an object"
                    )
                    continue
                for operation in ("add_key", "all_keys_lost"):
                    if operation not in operations:
                        errors.append(
                            f"{rel_dir}/procedures.json: {generation_id} missing {operation}"
                        )
                        continue
                    record = operations[operation]
                    if not isinstance(record, dict):
                        errors.append(
                            f"{rel_dir}/procedures.json: {generation_id}.{operation} must be an object"
                        )
                        continue
                    if not any(record.get(field) for field in ("method", "summary", "programming_method")):
                        errors.append(
                            f"{rel_dir}/procedures.json: {generation_id}.{operation} has no readable method"
                        )

    declared_dirs = set(models)
    actual_dirs = {
        path.name
        for path in VW_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    }
    for undeclared in sorted(actual_dirs - declared_dirs):
        errors.append(f"Volkswagen model directory is not declared in manifest: {undeclared}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print(f"Volkswagen validation failed with {len(errors)} issue(s):")
        for issue in errors:
            print(f"- {issue}")
        return 1

    print("Volkswagen validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
