#!/usr/bin/env python3
"""audit-sources.py — deterministic audit of the canonical Sources data + generated HTML.

Verifies, exiting non-zero on any failure:
  1. Coverage — every credits-bearing page has a data/sources/**.json file, and every data
     file maps to an existing page that still has a credits section.
  2. External-only — every source `url` is an external https?:// reference (no relative, #...,
     or bare .html site links), and no <a href> anywhere in a credits block points internally.
  3. No drift — regenerating each page from its data file is a no-op (HTML == data).
  4. Schema — each data file has page/lead/sources, and each source has label/what/url/display.

Usage:
    python3 scripts/audit-sources.py            # audit everything
    python3 scripts/audit-sources.py --quiet    # only print the summary + failures
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources_lib as L  # noqa: E402

ANY_A_HREF_RE = re.compile(r'<a\s[^>]*href="([^"]*)"')
EXTERNAL_RE = re.compile(r'^https?://', re.I)


def is_external(url):
    return bool(EXTERNAL_RE.match(url))


def main():
    quiet = "--quiet" in sys.argv
    fails = []

    pages = list(L.iter_credits_pages())
    page_rels = {str(p.resolve().relative_to(L.ROOT)).replace("\\", "/") for p in pages}
    data_files = sorted(L.DATA_DIR.rglob("*.json"))

    # 1. coverage
    data_pages = set()
    for df in data_files:
        try:
            data = json.loads(df.read_text(encoding="utf-8"))
        except Exception as e:
            fails.append(f"[schema] {df}: invalid JSON ({e})")
            continue
        # 4. schema
        for key in ("page", "lead", "sources"):
            if key not in data:
                fails.append(f"[schema] {df.name}: missing '{key}'")
        page_rel = data.get("page", "")
        data_pages.add(page_rel)
        expected = L.page_to_data_path(page_rel).resolve()
        if expected != df.resolve():
            fails.append(f"[coverage] {df.name}: 'page' {page_rel} maps to {expected.name}, "
                         f"not its own location")
        for i, s in enumerate(data.get("sources", [])):
            for key in ("label", "what", "url", "display"):
                if key not in s:
                    fails.append(f"[schema] {df.name} source #{i}: missing '{key}'")
            # 2. external-only (data)
            if "url" in s and not is_external(s["url"]):
                fails.append(f"[external] {page_rel} source #{i}: non-external url {s['url']!r}")

    for pr in page_rels - data_pages:
        fails.append(f"[coverage] page has credits but no data file: {pr}")
    for dp in data_pages - page_rels:
        fails.append(f"[coverage] data file references missing/credit-less page: {dp}")

    # 2. external-only (HTML) + 3. no drift
    for page in pages:
        text = L.read_text(page)
        parsed = L.parse_credits(text)
        page_rel = str(page.resolve().relative_to(L.ROOT)).replace("\\", "/")
        block = "".join(text.splitlines(keepends=True)[parsed["start"]:parsed["end"] + 1])
        for href in ANY_A_HREF_RE.findall(block):
            if not is_external(href):
                fails.append(f"[external] {page_rel}: internal link in credits: {href!r}")
        # drift
        df = L.page_to_data_path(page_rel)
        if df.exists():
            data = json.loads(df.read_text(encoding="utf-8"))
            rebuilt = L.render_credits(parsed["indent"], parsed["sec_num"], data["lead"],
                                       data["sources"], L.detect_eol(text),
                                       tag=data.get("tag"))
            current = block if block.endswith(L.detect_eol(text)) else block + L.detect_eol(text)
            if rebuilt != current:
                fails.append(f"[drift] {page_rel}: HTML credits differ from data "
                             f"(run build-sources.py)")

    print(f"pages: {len(pages)}   data files: {len(data_files)}   failures: {len(fails)}")
    if fails:
        print()
        for f in fails:
            print(f"  FAIL {f}")
        sys.exit(1)
    if not quiet:
        print("OK — every credits page has canonical data, all sources external, no drift.")


if __name__ == "__main__":
    main()
