#!/usr/bin/env python3
"""
strip-page-accents.py — remove every per-page accent override <style> block.

Each themed guide carries a single page-level style block of the form:

    <style>:root{--accent:var(--maroon-lt);--accent-lt:var(--maroon-lt);--accent-deep:var(--maroon);
      --accent-soft:rgba(177,49,64,.4);--accent-glow:rgba(177,49,64,.10);}</style>

That block is the *only* thing it does: it re-tints the masthead `.role` tag away from
the design-system default (amber). This script deletes those blocks (and their trailing
newline) so every page falls back to the DS default accent. The accent *feature* itself
lives entirely in design-system/css/ed-blackbox.css and is left untouched — any future
page can still set `--accent` in a page <style> and it will work.

Bespoke page <style> blocks that do NOT define `--accent` (index.html grids,
checklist/materials/modules table layouts) are matched by content and left alone.

Usage:
    python3 scripts/strip-page-accents.py            # apply
    python3 scripts/strip-page-accents.py --dry-run  # report only, no writes
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUIDES = REPO / "guides"

# A <style> block whose body opens with `:root{--accent:` — the accent override shape.
# Non-greedy to a single closing </style>; swallow one trailing newline if present.
ACCENT_BLOCK = re.compile(
    r"[ \t]*<style>:root\{--accent:.*?</style>\n?",
    re.DOTALL,
)


def main() -> int:
    dry = "--dry-run" in sys.argv[1:]
    changed = 0
    for path in sorted(GUIDES.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        new, n = ACCENT_BLOCK.subn("", text)
        if n == 0:
            continue
        if n > 1:
            print(f"!! {path.relative_to(REPO)}: {n} accent blocks (expected 1)")
        rel = path.relative_to(REPO)
        if dry:
            print(f"would strip  {rel}")
        else:
            path.write_text(new, encoding="utf-8")
            print(f"stripped     {rel}")
        changed += 1

    verb = "would strip" if dry else "stripped"
    print(f"\n{verb} accent override blocks from {changed} page(s).")
    if not dry and changed:
        print("Page accent feature remains available via ed-blackbox.css (--accent* group).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
