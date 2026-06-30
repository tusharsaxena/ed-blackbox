#!/usr/bin/env python3
"""delink-blueprint-module-refs.py — strip ship/role-specific chrome from blueprints.html.

On guides/engineering/blueprints.html the apply-hyperlinks pass wraps module/blueprint
*type* names in <a> links (group labels, per-card tags, experimental descriptions, and a
few mis-linked material-name cells). Those references are ship/role-agnostic in this
reference catalogue, so we unwrap them — while KEEPING the engineer links (engineers.html#)
in the per-grade rows, which are genuinely useful.

It also removes the "★ recommended" experimental badge everywhere: which experimental is
"recommended" is ship/role specific and doesn't belong on the generic blueprint reference.

Transforms (byte-preserving otherwise):
  1. <a href="modules.html#…">TEXT</a>      -> TEXT
  2. <a href="blueprints.html#…">TEXT</a>   -> TEXT
  3. <span class="bp-rec">★ recommended</span>  (+ one leading space) -> removed

Engineer links (engineers.html#…) are left untouched.

Note: blueprints.html is a link SOURCE for apply-hyperlinks.py, so a future hyperlink pass
could re-add these. If that becomes a problem, mark the relevant spans/cells class="nolink".

Usage:  python3 scripts/delink-blueprint-module-refs.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "guides" / "engineering" / "blueprints.html"


def main() -> int:
    html = TARGET.read_text(encoding="utf-8")
    orig = html

    mod_links = len(re.findall(r'<a href="modules\.html#[^"]*">', html))
    bp_links = len(re.findall(r'<a href="blueprints\.html#[^"]*">', html))
    eng_before = len(re.findall(r'<a href="engineers\.html#[^"]*">', html))
    rec_tags = len(re.findall(r'<span class="bp-rec">', html))

    # 1 & 2: unwrap module / blueprint type links (keep the visible text)
    html = re.sub(r'<a href="modules\.html#[^"]*">(.*?)</a>', r"\1", html)
    html = re.sub(r'<a href="blueprints\.html#[^"]*">(.*?)</a>', r"\1", html)

    # 3: drop the "★ recommended" badge plus one leading space if present
    html = re.sub(r' ?<span class="bp-rec">[^<]*</span>', "", html)

    eng_after = len(re.findall(r'<a href="engineers\.html#[^"]*">', html))

    if html == orig:
        print("No changes — already de-linked.")
        return 0

    TARGET.write_text(html, encoding="utf-8")
    print(f"Updated {TARGET.relative_to(ROOT)}")
    print(f"  module links unwrapped     : {mod_links}")
    print(f"  blueprint links unwrapped  : {bp_links}")
    print(f"  recommended badges removed : {rec_tags}")
    print(f"  engineer links kept        : {eng_before} -> {eng_after}")
    if eng_before != eng_after:
        print("  WARNING: engineer link count changed — investigate!", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
