#!/usr/bin/env python3
"""Generate a conservative, evidence-neutral repository quality audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VEHICLES = ROOT / "database" / "vehicles"
REPORT = ROOT / "reports" / "repository_quality_backlog.json"
REQUIRED_MODEL_FILES = {
    "manifest.json", "models.json", "modules.json", "notes.json", "photos.json",
    "procedures.json", "service_functions.json", "wiring.json",
}
LINK_FIELDS = {
    "platform": ("platform", "platform_id", "security_platform_id"),
    "immobiliser_family": ("immobiliser_family", "immobiliser_family_id", "immobiliser_system_id"),
    "key_family": ("key_family", "key_family_id", "key_type_id"),
    "transponder_family": ("transponder_family", "transponder_family_id", "transponder_id"),
    "blade_family": ("blade_family", "blade_family_id", "blade_id"),
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def walk(node: Any):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the canonical JSON report")
    args = parser.parse_args()

    json_files = sorted((ROOT / "database").rglob("*.json"))
    parse_errors: list[str] = []
    parsed: dict[Path, Any] = {}
    mojibake: list[str] = []
    note_occurrences: dict[str, set[str]] = defaultdict(set)
    terminology = Counter()
    for path in json_files:
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in ("Ã", "Â", "â€", "Å ")):
            mojibake.append(path.relative_to(ROOT).as_posix())
        try:
            data = json.loads(text)
            parsed[path] = data
        except json.JSONDecodeError:
            parse_errors.append(path.relative_to(ROOT).as_posix())
            continue
        for obj in walk(data):
            for key, value in obj.items():
                if key in {"note", "notes", "description", "warning"} and isinstance(value, str) and len(value) >= 30:
                    note_occurrences[" ".join(value.split())].add(path.relative_to(ROOT).as_posix())
                if isinstance(value, str):
                    low = value.lower()
                    for term in ("keyless", "proximity", "passive", "smart key", "kessy"):
                        if term in low:
                            terminology[term] += 1

    manufacturer_dirs = sorted(p for p in VEHICLES.iterdir() if p.is_dir())
    model_dirs = sorted(
        p for manufacturer in manufacturer_dirs for p in manufacturer.iterdir()
        if p.is_dir() and (p / "manifest.json").exists()
    )
    missing_files: dict[str, list[str]] = {}
    missing_links = Counter()
    link_examples: dict[str, list[str]] = defaultdict(list)
    missing_keywords: list[str] = []
    missing_service_functions: list[str] = []
    for model_dir in model_dirs:
        rel_dir = model_dir.relative_to(ROOT).as_posix()
        absent = sorted(REQUIRED_MODEL_FILES - {p.name for p in model_dir.glob("*.json")})
        if absent:
            missing_files[rel_dir] = absent
        manifest = parsed.get(model_dir / "manifest.json", {})
        model_data = parsed.get(model_dir / "models.json", {})
        combined = json.dumps([manifest, model_data], ensure_ascii=False).lower()
        if "search_keywords" not in combined and "keywords" not in combined:
            missing_keywords.append(rel_dir)
        if not (model_dir / "service_functions.json").exists():
            missing_service_functions.append(rel_dir)
        for family, aliases in LINK_FIELDS.items():
            if not any(f'"{alias}"' in combined for alias in aliases):
                missing_links[family] += 1
                if len(link_examples[family]) < 10:
                    link_examples[family].append(rel_dir)

    duplicates = [
        {"text": text, "files": sorted(files), "file_count": len(files)}
        for text, files in note_occurrences.items() if len(files) > 1
    ]
    duplicates.sort(key=lambda item: (-item["file_count"], item["text"]))

    backlog = [
        {
            "priority": 1, "improvement": "Define a canonical metadata terminology vocabulary and aliases",
            "benefit": "High: improves search consistency without changing technical claims",
            "files_affected": "Schema/reference vocabulary plus records selected after review",
            "effort": "Medium", "risk": "Medium",
            "evidence": {"observed_term_counts": dict(terminology)},
        },
        {
            "priority": 2, "improvement": "Add explicit family links where architecture evidence already exists",
            "benefit": "High: enables safe reuse of verified platform, immobiliser, key, transponder and blade facts",
            "files_affected": f"Up to {sum(missing_links.values())} model/family link opportunities (not deduplicated)",
            "effort": "High", "risk": "Medium",
            "evidence": {"missing_by_family": dict(missing_links), "examples": dict(link_examples)},
        },
        {
            "priority": 3, "improvement": "Consolidate repeated prose into shared notes with references",
            "benefit": "Medium: reduces drift and duplicated maintenance",
            "files_affected": len({p for item in duplicates for p in item["files"]}),
            "effort": "High", "risk": "Medium",
            "evidence": {"duplicate_groups": len(duplicates), "largest_groups": duplicates[:10]},
        },
        {
            "priority": 4, "improvement": "Backfill display_name and schema_version warnings by file family",
            "benefit": "Medium: makes validator output actionable and improves UI labels",
            "files_affected": "Measured by scripts/validate_database.py output",
            "effort": "High", "risk": "Low",
        },
        {
            "priority": 5, "improvement": "Review service-function coverage against evidence",
            "benefit": "Medium: improves workshop usefulness",
            "files_affected": len(missing_service_functions), "effort": "High", "risk": "High",
            "evidence": {"structurally_missing_files": missing_service_functions[:20]},
        },
    ]
    report = {
        "schema_version": "1.0",
        "generated_at": date.today().isoformat(),
        "scope": "Evidence-neutral repository quality audit; no technical facts inferred",
        "summary": {
            "manufacturers": len(manufacturer_dirs), "model_directories": len(model_dirs),
            "json_files": len(json_files), "json_parse_errors": len(parse_errors),
            "model_directories_missing_required_files": len(missing_files),
            "files_with_possible_mojibake": len(mojibake),
            "duplicate_note_groups": len(duplicates),
            "models_without_explicit_search_keywords": len(missing_keywords),
            "missing_family_links": dict(missing_links),
        },
        "parse_errors": parse_errors,
        "missing_required_files": missing_files,
        "possible_mojibake_files": mojibake,
        "implemented_low_risk_high_benefit": [
            {
                "improvement": "Support repository-root-relative and manifest-relative manifest links",
                "benefit": "Removed false missing-manifest diagnostics while retaining legacy behaviour",
                "files_affected": 1, "effort": "Low", "risk": "Low",
            },
            {
                "improvement": "Add deterministic non-technical UK model search keywords",
                "benefit": "All model manifests are discoverable by manufacturer/model names, IDs, UK and RHD",
                "files_affected": len(model_dirs), "effort": "Medium", "risk": "Low",
            },
            {
                "improvement": "Replace stale repository phase status",
                "benefit": "Top-level manifest accurately describes completion of Phase 2 architecture verification",
                "files_affected": 1, "effort": "Low", "risk": "Low",
            },
        ],
        "prioritised_backlog": backlog,
    }
    output = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        REPORT.write_text(output, encoding="utf-8")
        print(f"wrote {REPORT.relative_to(ROOT)}")
    else:
        print(output)
    return 1 if parse_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
