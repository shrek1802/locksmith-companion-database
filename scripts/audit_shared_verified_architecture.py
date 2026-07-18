#!/usr/bin/env python3
"""Index source-backed verified claims that may be candidates for architecture reuse.

This audit is intentionally conservative. Manufacturer/model manifest status is not
technical evidence, and a claim is not reusable merely because another JSON record
contains the same wording. Reuse candidates require a record-level verified status
and at least two traceable source references. Human review is still required before
inheritance because matching names do not prove matching hardware or software.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "database"
REPORT = ROOT / "reports" / "shared_verified_architecture_audit.json"

VERIFIED = {"verified", "fully_verified"}
SOURCE_KEYS = {"sources", "source", "references", "evidence"}
ARCHITECTURE_KEYS = {
    "platform",
    "platform_id",
    "immobiliser_family",
    "immobiliser_family_id",
    "immobiliser_system",
    "bcm",
    "dashboard",
    "instrument_cluster",
    "kessy",
    "key_type",
    "blade",
    "blade_profile",
    "frequency",
    "frequency_mhz",
    "transponder",
    "transponder_type",
    "tool_support",
}


def walk(value: Any, path: tuple[str, ...] = ()):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk(child, (*path, str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, (*path, str(index)))


def normalise_status(value: Any) -> str:
    return str(value).strip().lower().replace("-", "_").replace(" ", "_")


def source_refs(record: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for key in SOURCE_KEYS:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            refs.append(value.strip())
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.strip():
                    refs.append(item.strip())
                elif isinstance(item, dict):
                    ref = item.get("url") or item.get("source") or item.get("id")
                    if isinstance(ref, str) and ref.strip():
                        refs.append(ref.strip())
    return sorted(set(refs))


def main() -> int:
    candidates: list[dict[str, Any]] = []
    rejected: Counter[str] = Counter()
    files_scanned = 0

    for path in sorted(DATABASE.rglob("*.json")):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            rejected["unreadable_json"] += 1
            continue
        files_scanned += 1
        for json_path, record in walk(document):
            if not record:
                continue
            status = normalise_status(
                record.get("verification_status")
                or record.get("verification_state")
                or record.get("status")
            )
            if status not in VERIFIED:
                continue
            claims = {key: record[key] for key in ARCHITECTURE_KEYS if key in record}
            if not claims:
                rejected["no_architecture_claim"] += 1
                continue
            refs = source_refs(record)
            if len(refs) < 2:
                rejected["fewer_than_two_sources"] += 1
                continue
            candidates.append({
                "file": path.relative_to(ROOT).as_posix(),
                "json_path": "/".join(json_path),
                "status": status,
                "claims": claims,
                "sources": refs,
                "reuse_status": "human_review_required",
                "reuse_warning": "Confirm identical part/hardware/software and UK RHD applicability before inheritance.",
            })

    report = {
        "schema_version": "1.0",
        "generated_at": "2026-07-18",
        "scope": "UK RHD repository-wide architecture reuse candidates",
        "policy": {
            "manifest_status_is_evidence": False,
            "minimum_traceable_sources": 2,
            "automatic_inheritance_allowed": False,
        },
        "counts": {
            "json_files_scanned": files_scanned,
            "reuse_candidates": len(candidates),
            "rejected": dict(sorted(rejected.items())),
        },
        "candidates": candidates,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], indent=2))
    print(f"report: {REPORT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
