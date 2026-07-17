#!/usr/bin/env python3
"""Build an evidence-first research queue from missing Ford security-access data."""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "reports" / "ford_security_access_audit.json"
OUTPUT = ROOT / "reports" / "ford_security_access_research_queue.json"


def priority(row: dict) -> str:
    year_from = row.get("year_from")
    if isinstance(year_from, int) and year_from >= 2018:
        return "high"
    if isinstance(year_from, int) and year_from >= 2008:
        return "medium"
    return "standard"


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    missing = audit.get("missing", [])
    groups: dict[str, list[dict]] = defaultdict(list)

    for row in missing:
        item = dict(row)
        item["priority"] = priority(item)
        item["research_requirement"] = (
            "Verify the exact UK-market security-access route from authoritative evidence; "
            "do not infer it from OBD programming support."
        )
        groups[item["priority"]].append(item)

    order = {"high": 0, "medium": 1, "standard": 2}
    for rows in groups.values():
        rows.sort(key=lambda r: (r.get("model") or "", r.get("year_from") or 0, r.get("variant") or ""))

    queue = {
        "policy": "Evidence first: missing values remain missing until the exact UK security-access route is verified.",
        "source_report": "reports/ford_security_access_audit.json",
        "counts": {
            "total": len(missing),
            "by_priority": dict(Counter(priority(row) for row in missing)),
            "by_model": dict(sorted(Counter(row.get("model") or "Unknown" for row in missing).items())),
        },
        "research_order": [
            {"priority": key, "records": groups[key]}
            for key in sorted(groups, key=lambda value: order[value])
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(queue["counts"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
