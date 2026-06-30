#!/usr/bin/env python3
"""
add-breadcrumb-subsection.py — Insert the index SUB-SECTION crumb into every
guide page's breadcrumb, turning

    Home › <Main Section> › <Page Title>
into
    Home › <Main Section> › <Sub Section> › <Page Title>

The sub-section is the index sub-head the page lives under (e.g. by-role pages →
"Best Ships by Role", dossiers → "Ship Dossiers", farms → "Materials & Farming").
The new crumb links to that sub-head's anchor on index.html. Idempotent.

The page → (main, sub) map is built at runtime by parsing the landing-page
generator (generate-guides-index.sh) — each `card` line under a `<section>` /
`<h3 class="subhead">`, plus the auto-discovered ship dossiers under "Ship
Dossiers" — so it always tracks the index IA. No external data file needed.

Usage:
  python3 scripts/add-breadcrumb-subsection.py [--files a.html ...] [--dry-run]
Paths resolve relative to the repo root.
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GEN = REPO / "scripts" / "generate-guides-index.sh"


def build_map():
    """page_url -> {main, main_id, sub, sub_id}, parsed from the index generator."""
    gen = GEN.read_text(encoding="utf-8")
    mains = {}
    for m in re.finditer(r'<section id="(section-[^"]+)">\s*\n\s*<div class="sec-head">.*?<h2>([^<]+)</h2>', gen, re.S):
        mains[m.group(1)] = m.group(2)
    mapping = {}
    cur_main = cur_sub = cur_sub_id = None
    for line in gen.splitlines():
        ms = re.search(r'<section id="(section-[^"]+)">', line)
        if ms:
            cur_main = mains.get(ms.group(1), ms.group(1)); cur_sub = cur_sub_id = None
        hs = re.search(r'<h3 class="subhead" id="(section-[^"]+)">([^<]+)</h3>', line)
        if hs:
            cur_sub_id, cur_sub = hs.group(1), hs.group(2)
        cm = re.match(r'card "([^"]+)"', line)
        if cm and cur_sub_id:
            mapping["guides/" + cm.group(1).split("#")[0]] = {
                "main": cur_main, "sub": cur_sub, "sub_id": cur_sub_id}
    # auto-discovered dossiers live under the "Ship Dossiers" sub-head
    for f in sorted((REPO / "guides/ships/dossiers").glob("*.html")):
        mapping[f.relative_to(REPO).as_posix()] = {
            "main": "Ships", "sub": "Ship Dossiers", "sub_id": "section-ship-dossiers"}
    return mapping


def apply_page(path: Path, info: dict, dry: bool):
    html = path.read_text(encoding="utf-8")
    nav_m = re.search(r'<nav class="breadcrumbs"[^>]*>.*?</nav>', html, re.S)
    if not nav_m:
        return "no-breadcrumb", False
    nav = nav_m.group(0)

    sub_id = info["sub_id"]
    base_m = re.search(r'<a href="([^"]*index\.html)">Home</a>', nav)
    if not base_m:
        return "no-home-href", False
    crumb = f'<a href="{base_m.group(1)}#{sub_id}">{info["sub"]}</a>'
    sub_re = r'<a href="[^"]*#' + re.escape(sub_id) + r'">[^<]*</a>'
    orig = nav

    # Step 1 — fresh page: insert the sub crumb right after the last separator,
    # before the current-page span (the trailing separator is added in step 2).
    if not re.search(sub_re, nav):
        nav = re.sub(
            r'(<span class="sep">›</span>\s*\n\s*)(<span class="current")',
            lambda m: m.group(1) + crumb + "\n  " + m.group(2), nav, count=1)

    # Step 2 — ensure a separator sits between the sub crumb and the current span.
    # Repairs an earlier insert that dropped this separator; no-op once correct.
    nav = re.sub(
        r'(' + sub_re + r')(\s*\n\s*)(<span class="current")',
        r'\1\2<span class="sep">›</span>\n  \3', nav, count=1)

    if nav == orig:
        return "noop", False
    status = "inserted" if re.search(sub_re, orig) is None else "repaired"
    html = html[:nav_m.start()] + nav + html[nav_m.end():]
    if not dry:
        path.write_text(html, encoding="utf-8")
    return status, True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    mapping = build_map()
    files = a.files if a.files else sorted(mapping.keys())

    n = wrote = 0
    for f in files:
        f = f.replace(str(REPO) + "/", "")
        if f not in mapping:
            print(f"  ?? not in map: {f}"); continue
        status, did = apply_page(REPO / f, mapping[f], a.dry_run)
        n += 1
        wrote += 1 if did else 0
        tag = "DRY " if a.dry_run else ("WROTE" if did else "·····")
        print(f"  {tag} {f:50} {status:14} {mapping[f]['main']} › {mapping[f]['sub']}")
    print(f"\n{'(dry-run) ' if a.dry_run else ''}{n} files, {wrote} changed")


if __name__ == "__main__":
    main()
