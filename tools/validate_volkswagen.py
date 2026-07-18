#!/usr/bin/env python3
"""Validate Volkswagen structure and report technical-verification progress.

Structural/schema errors fail CI. Evidence gaps are reported as progress items and do
not fail CI, because the validator must never decide whether a locksmith fact is true.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
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
DATA_FILES = sorted(REQUIRED_FILES - {"manifest.json"})
APPROVED_STATUS = {
    "supported",
    "conditional",
    "verification_required",
    "research_required",
    "not_supported",
    "research_in_progress",
    "to_be_verified",
    "fully_verified",
    "operation_specific_tool_support_added_with_conditions",
    "operation_specific_tool_support_partially_verified",
}
UNRESOLVED_STATUS = {
    "conditional",
    "verification_required",
    "research_required",
    "research_in_progress",
    "to_be_verified",
    "operation_specific_tool_support_added_with_conditions",
    "operation_specific_tool_support_partially_verified",
}
RESOLVED_STATUS = {"supported", "not_supported", "fully_verified"}
PLACEHOLDER_TEXT = {
    "research required",
    "verification required",
    "to be verified",
    "research_required",
    "verification_required",
    "to_be_verified",
}
RAW_PROCEDURE_PREFIX = "PROC_"
LOCATION_TERMS = ("location", "obd", "kessy", "access_start", "access-start", "sgw", "immobiliser")
TOOL_TERMS = ("tool", "autel", "obdstar", "xhorse", "lonsdor", "smart pro", "advanced diagnostics")
WIRING_TERMS = ("wiring", "bench", "pinout", "connection", "processor", "eeprom")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ValueError(f"Missing file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON: {path.relative_to(ROOT)} line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc


def walk_values(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, str(key))
            yield child_path, key, child
            yield from walk_values(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = (*path, str(index))
            yield child_path, str(index), child
            yield from walk_values(child, child_path)


def normalise_status(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def contains_term(path: tuple[str, ...], value: Any, terms: tuple[str, ...]) -> bool:
    haystack = " ".join(path).lower()
    if isinstance(value, str):
        haystack += " " + value.lower()
    return any(term in haystack for term in terms)


def empty_photo_collections(data: Any) -> int:
    count = 0
    for path, key, value in walk_values(data):
        if key in {"photos", "images", "assets"} and isinstance(value, list) and not value:
            count += 1
        elif len(path) == 2 and path[0] == "items" and isinstance(value, list) and not value:
            count += 1
    return count


def evidence_scan(model_id: str, model_dir: Path, evidence: dict[str, Any], errors: list[str]) -> None:
    model = evidence["models"][model_id]
    for filename in DATA_FILES:
        path = model_dir / filename
        try:
            data = load_json(path)
        except ValueError as exc:
            errors.append(str(exc))
            continue

        model["files_scanned"] += 1
        file_statuses: Counter[str] = Counter()
        file_placeholders = 0

        for json_path, key, value in walk_values(data):
            if key in {"status", "overall_status", "tool_support", "verification_status", "document_status"} and isinstance(value, str):
                status = normalise_status(value)
                file_statuses[status] += 1
                evidence["status_counts"][status] += 1
                model["status_counts"][status] += 1

                if status in UNRESOLVED_STATUS:
                    evidence["unresolved_total"] += 1
                    model["unresolved"] += 1
                    if contains_term(json_path, value, LOCATION_TERMS):
                        model["location_gaps"] += 1
                    if contains_term(json_path, value, TOOL_TERMS) or key == "tool_support":
                        model["tool_gaps"] += 1
                    if filename == "wiring.json" or contains_term(json_path, value, WIRING_TERMS):
                        model["wiring_gaps"] += 1
                elif status in RESOLVED_STATUS:
                    evidence["resolved_total"] += 1
                    model["resolved"] += 1

            if isinstance(value, str):
                text = value.strip().lower()
                if text in PLACEHOLDER_TEXT:
                    file_placeholders += 1
                    evidence["placeholder_total"] += 1
                    model["placeholders"] += 1

        if filename == "photos.json":
            empty = empty_photo_collections(data)
            model["empty_photo_groups"] += empty
            evidence["empty_photo_groups"] += empty

        if file_statuses or file_placeholders:
            model["files_with_evidence_items"].append(filename)

    model["fully_verified"] = (
        model["unresolved"] == 0
        and model["placeholders"] == 0
        and model["empty_photo_groups"] == 0
        and model["files_scanned"] == len(DATA_FILES)
        and model["resolved"] > 0
    )


def validate() -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    evidence: dict[str, Any] = {
        "models": defaultdict(lambda: {
            "files_scanned": 0,
            "files_with_evidence_items": [],
            "status_counts": Counter(),
            "resolved": 0,
            "unresolved": 0,
            "placeholders": 0,
            "empty_photo_groups": 0,
            "location_gaps": 0,
            "tool_gaps": 0,
            "wiring_gaps": 0,
            "fully_verified": False,
        }),
        "status_counts": Counter(),
        "resolved_total": 0,
        "unresolved_total": 0,
        "placeholder_total": 0,
        "empty_photo_groups": 0,
    }

    try:
        manufacturer = load_json(VW_MANIFEST)
    except ValueError as exc:
        return [str(exc)], evidence

    if manufacturer.get("schema_version") != "2.1":
        errors.append("Volkswagen manifest schema_version must be 2.1")

    maker = manufacturer.get("manufacturer", {})
    if maker.get("market") != "UK" or maker.get("drive_side") != "RHD":
        errors.append("Volkswagen manifest must declare UK market and RHD drive side")

    models = manufacturer.get("models")
    if not isinstance(models, dict) or not models:
        errors.append("Volkswagen manifest contains no model map")
        return errors, evidence

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

        try:
            model_manifest = load_json(model_dir / "manifest.json")
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

        expected_refs = {
            "models": "models.json",
            "procedures": "procedures.json",
            "modules": "modules.json",
            "wiring": "wiring.json",
            "service_functions": "service_functions.json",
            "notes": "notes.json",
            "photos": "photos.json",
        }
        files = model_manifest.get("files", {})
        for key, filename in expected_refs.items():
            if files.get(key) != filename:
                errors.append(f"{rel_dir}/manifest.json: files.{key} must reference {filename}")

        try:
            models_data = load_json(model_dir / "models.json")
            procedures_data = load_json(model_dir / "procedures.json")
        except ValueError as exc:
            errors.append(str(exc))
            continue

        for _, key, value in walk_values(models_data):
            if key == "market" and value != "UK":
                errors.append(f"{rel_dir}/models.json: non-UK market value {value!r}")
            if key == "drive_side" and value != "RHD":
                errors.append(f"{rel_dir}/models.json: non-RHD drive_side value {value!r}")

        procedure_items = procedures_data.get("items")
        if procedure_items is None:
            procedure_items = procedures_data.get("procedures")
        if procedure_items is None:
            errors.append(f"{rel_dir}/procedures.json: missing top-level 'items' procedure records")
            procedure_items = {}

        for _, key, value in walk_values(procedures_data):
            if isinstance(value, str) and value.startswith(RAW_PROCEDURE_PREFIX):
                errors.append(f"{rel_dir}/procedures.json: raw procedure ID remains: {value}")
            if key in {"status", "overall_status", "tool_support"} and isinstance(value, str):
                status = normalise_status(value)
                if status not in APPROVED_STATUS:
                    errors.append(f"{rel_dir}/procedures.json: unapproved status value {value!r}")

        if isinstance(procedure_items, dict):
            for generation_id, operations in procedure_items.items():
                if not isinstance(operations, dict):
                    errors.append(f"{rel_dir}/procedures.json: {generation_id} must be an object")
                    continue
                for operation in ("add_key", "all_keys_lost"):
                    if operation not in operations:
                        errors.append(f"{rel_dir}/procedures.json: {generation_id} missing {operation}")
                        continue
                    record = operations[operation]
                    if not isinstance(record, dict):
                        errors.append(f"{rel_dir}/procedures.json: {generation_id}.{operation} must be an object")
                        continue
                    if not any(record.get(field) for field in ("method", "summary", "programming_method")):
                        errors.append(f"{rel_dir}/procedures.json: {generation_id}.{operation} has no readable method")

        evidence_scan(model_id, model_dir, evidence, errors)

    declared_dirs = set(models)
    actual_dirs = {
        path.name for path in VW_ROOT.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    }
    for undeclared in sorted(actual_dirs - declared_dirs):
        errors.append(f"Volkswagen model directory is not declared in manifest: {undeclared}")

    evidence["model_count"] = len(models)
    return errors, evidence


def print_evidence_report(evidence: dict[str, Any]) -> None:
    resolved = evidence["resolved_total"]
    unresolved = evidence["unresolved_total"]
    tracked = resolved + unresolved
    percentage = round((resolved / tracked) * 100, 1) if tracked else 0.0
    models = evidence["models"]
    fully_verified = sum(1 for item in models.values() if item["fully_verified"])

    print("\nVolkswagen technical-verification progress")
    print("==========================================")
    print(f"Models fully verified: {fully_verified} / {evidence.get('model_count', len(models))}")
    print(f"Resolved evidence statuses: {resolved}")
    print(f"Unresolved evidence statuses: {unresolved}")
    print(f"Tracked-status completion: {percentage}%")
    print(f"Literal verification placeholders: {evidence['placeholder_total']}")
    print(f"Empty photo groups: {evidence['empty_photo_groups']}")

    if evidence["status_counts"]:
        print("\nStatus totals:")
        for status, count in sorted(evidence["status_counts"].items()):
            print(f"- {status}: {count}")

    ranked = sorted(
        models.items(),
        key=lambda pair: (
            pair[1]["unresolved"] + pair[1]["placeholders"] + pair[1]["empty_photo_groups"],
            pair[0],
        ),
        reverse=True,
    )
    print("\nOutstanding work by model (highest first):")
    for model_id, item in ranked:
        outstanding = item["unresolved"] + item["placeholders"] + item["empty_photo_groups"]
        print(
            f"- {model_id}: outstanding={outstanding}, unresolved_statuses={item['unresolved']}, "
            f"placeholders={item['placeholders']}, empty_photo_groups={item['empty_photo_groups']}, "
            f"tool_gaps={item['tool_gaps']}, location_gaps={item['location_gaps']}, "
            f"wiring_gaps={item['wiring_gaps']}, resolved={item['resolved']}"
        )

    print("\nNote: these are evidence-work indicators, not proof that any vehicle claim is correct.")


def main() -> int:
    errors, evidence = validate()
    if errors:
        print(f"Volkswagen validation failed with {len(errors)} structural issue(s):")
        for issue in errors:
            print(f"- {issue}")
    else:
        print("Volkswagen structural validation passed.")

    print_evidence_report(evidence)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
