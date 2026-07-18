#!/usr/bin/env python3
"""Attach Silca's displayed transponder code to pre-matched proximity rows."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader

PRODUCT = re.compile(r"^[A-Z0-9-]{3,20}(?:P|R|S)\d{2}$")
TP = re.compile(r"^\s*\d+\s+([0-9A-Z-]{2,8})\s*$")


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("*", "").strip()).casefold()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--applications", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    wanted = json.loads(args.applications.read_text(encoding="utf-8"))
    by_raw: dict[str, list[dict]] = {}
    for row in wanted:
        by_raw.setdefault(clean(row["raw"]), []).append(row)
    results, unresolved = [], []
    for page_number, page in enumerate(PdfReader(str(args.pdf)).pages, 1):
        lines = [x.strip() for x in (page.extract_text() or "").splitlines() if x.strip()]
        products = [(i, line) for i, line in enumerate(lines) if PRODUCT.match(line)]
        codes = [(i, m.group(1).upper()) for i, line in enumerate(lines) if (m := TP.match(line))]
        ordered_codes = {ref: codes[n][1] for n, (_, ref) in enumerate(products)} if len(products) == len(codes) else {}
        for i, line in enumerate(lines):
            matches = by_raw.get(clean(line), [])
            for original in matches:
                blade = original["blade"].replace("-", "").upper()
                candidates = [(abs(i - pi), pi, ref) for pi, ref in products if blade in ref.replace("-", "").upper()]
                if not candidates:
                    unresolved.append({**original, "source_page": page_number, "reason": "product_reference_not_recovered"})
                    continue
                _, pi, ref = min(candidates)
                if ref in ordered_codes:
                    code, distance = ordered_codes[ref], 0
                else:
                    code_candidates = [(abs(pi - ci), code) for ci, code in codes if abs(pi - ci) <= 12]
                    if code_candidates:
                        distance, code = min(code_candidates)
                    else:
                        code = None
                if code is None:
                    unresolved.append({**original, "source_page": page_number, "product_reference": ref, "reason": "transponder_code_not_recovered"})
                    continue
                results.append({**original, "source_page": page_number, "product_reference": ref, "transponder_code": code, "association_distance": distance})
    # Deduplicate because repeated compatibility lines can occur in PDF extraction.
    unique = {}
    for row in results:
        key = (row["path"], row["raw"], row["key_variant_scope"], row["transponder_code"])
        unique[key] = row
    args.output.write_text(json.dumps({"applications": list(unique.values()), "unresolved": unresolved}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"matched": len(unique), "unresolved": len(unresolved), "codes": sorted({x["transponder_code"] for x in unique.values()})}))


if __name__ == "__main__":
    main()
