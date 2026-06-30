#!/usr/bin/env python3
"""update-dossier-titles.py — set every ship dossier's <title> to the canonical form.

    <Ship> · <Role> · Ship Dossier | E:D Black Box

The <Ship> name and <Role> label are read from the dossier's own masthead
(`<h1 class="title"><span>Ship</span><span class="role …">Role</span></h1>`) so the
title always matches what the page displays. `·` is written as the `&middot;` entity, the
form already used in these titles.

Idempotent: re-running yields the same titles. Edits guides/ships/dossiers/*.html in place.

Usage:
    python3 scripts/update-dossier-titles.py            # update all dossiers
    python3 scripts/update-dossier-titles.py --check    # report what would change, write nothing
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOSSIERS = ROOT / "guides" / "ships" / "dossiers"

TITLE_RE = re.compile(r"<title>.*?</title>", re.DOTALL)
# <h1 class="title"><span>Federal Corvette</span><span class="role ac-role-combat">Combat</span></h1>
MASTHEAD_RE = re.compile(
    r'<h1 class="title">\s*<span>(?P<ship>[^<]+)</span>\s*'
    r'<span class="role[^"]*">(?P<role>[^<]+)</span>'
)


def main() -> int:
    check = "--check" in sys.argv
    files = sorted(DOSSIERS.glob("*.html"))
    if not files:
        print("no dossier files found")
        return 1

    changed = 0
    for f in files:
        html = f.read_text(encoding="utf-8")
        m = MASTHEAD_RE.search(html)
        if not m:
            print(f"  SKIP (no masthead title/role): {f.name}")
            continue
        ship = m.group("ship").strip()
        role = m.group("role").strip()
        new_title = f"<title>{ship} &middot; {role} &middot; Ship Dossier | E:D Black Box</title>"

        new_html, n = TITLE_RE.subn(new_title, html, count=1)
        if n != 1:
            print(f"  SKIP (no <title>): {f.name}")
            continue
        if new_html != html:
            changed += 1
            cur = TITLE_RE.search(html).group(0)
            print(f"  {f.name}\n      - {cur}\n      + {new_title}")
            if not check:
                f.write_text(new_html, encoding="utf-8")

    verb = "would change" if check else "updated"
    print(f"\n{verb} {changed} of {len(files)} dossier titles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
