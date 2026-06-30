#!/usr/bin/env python3
"""
verify-title-blocks.py — Verify that pages' title blocks match the reviewed
workbook targets after apply-title-blocks.py has run.

For each file it re-reads the live <title> + masthead and checks:
  - <title> equals the target title_full
  - .kicker equals the rebuilt "A // B"
  - .masthead-meta is exactly 2 spans: bolded label + "Updated <b>YYYY-MM-DD</b>"
  - h1.title equals the rebuilt h1 IFF a user-modelled h1 field changed
  - p.subtitle is gone when the target subtitle is blank
  - no bare ampersands and no Excel-format dates survive in the masthead/title

Usage:
  python3 scripts/verify-title-blocks.py [--files a.html b.html ...]
Exit code is non-zero if any file FAILS. Reuses the build logic from
apply-title-blocks.py so the two can never drift.
"""
import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "scripts" / "out" / "edited-rows.json"

# import the sibling apply module (hyphenated filename -> load by path)
_spec = importlib.util.spec_from_file_location("apply_tb", REPO / "scripts" / "apply-title-blocks.py")
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def check(path: Path, cur, n):
    html = path.read_text(encoding="utf-8")
    fails = []

    title_m = re.search(r'<title>.*?</title>', html)
    if not title_m or title_m.group(0) != f"<title>{n['title_full']}</title>":
        fails.append(f"title is {title_m.group(0) if title_m else None!r}, want {n['title_full']!r}")

    mast = re.search(r'<header class="masthead">.*?</header>', html, re.S)
    if not mast:
        return ["no masthead"]
    mh = mast.group(0)

    kick = re.search(r'<div class="kicker">.*?</div>', mh, re.S)
    want_k = A.build_kicker(n['kicker_a'], n['kicker_b'])
    if not kick or kick.group(0) != want_k:
        fails.append(f"kicker mismatch -> {kick.group(0) if kick else None!r}")

    # meta: exactly two spans, bolded label + Updated date
    meta = re.search(r'<div class="masthead-meta">(.*?)</div>', mh, re.S)
    if meta:
        spans = re.findall(r'<span>(.*?)</span>', meta.group(1), re.S)
        spans = [s.strip() for s in spans]
        want = [A.bold_label(n['meta_label']), f"Updated <b>{n['meta_updated']}</b>"]
        if spans != want:
            fails.append(f"meta spans {spans} != {want}")
    else:
        fails.append("no masthead-meta")

    if (cur['h1_lead'], cur['h1_accent'], cur['h1_role']) != (n['h1_lead'], n['h1_accent'], n['h1_role']):
        h1 = re.search(r'<h1 class="title">.*?</h1>', mh, re.S)
        want_h1 = A.build_h1(n['h1_lead'], n['h1_accent'], n['h1_role'], h1.group(0) if h1 else "")
        if not h1 or h1.group(0) != want_h1:
            fails.append(f"h1 mismatch -> {h1.group(0) if h1 else None!r}")

    if not n['subtitle'].strip() and re.search(r'<p class="subtitle">', mh):
        fails.append("subtitle still present")

    if re.search(r'&(?!#?\w+;)', f"{title_m.group(0) if title_m else ''}{mh}"):
        fails.append("bare ampersand in title/masthead")
    if re.search(r'Updated <b>\d{1,2}/\d{1,2}/\d{4}</b>', mh):
        fails.append("Excel-format date survived")

    return fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=None)
    a = ap.parse_args()
    rows = {r['file']: r for r in json.loads(DATA.read_text(encoding="utf-8"))}
    targets = a.files if a.files else list(rows.keys())

    passed = failed = 0
    for f in targets:
        f = f.replace(str(REPO) + "/", "")
        if f not in rows:
            print(f"  ?? not in workbook: {f}"); failed += 1; continue
        cur = {k: ("" if rows[f]['cur'][k] is None else str(rows[f]['cur'][k])).strip() for k in A.ELEM}
        n = A.correct(rows[f])
        fails = check(REPO / f, cur, n)
        if fails:
            failed += 1
            print(f"  FAIL {f}")
            for x in fails:
                print(f"        - {x}")
        else:
            passed += 1
            print(f"  PASS {f}")
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
