#!/usr/bin/env python3
"""
bold-roster-stat-labels.py — bold the ship name in by-role roster stat tiles.

The §02 "How These Ships Are Scored" stat-grid on each guides/ships/by-role/<role>.html
uses tiles shaped like:

    <div class="stat"><div class="n">88</div><div class="l">Anaconda<small>the ceiling</small></div></div>

The ship name and its descriptor run together ("Anacondathe ceiling"). This wraps the name
in <b> (no trailing space); the CSS (`.stat .l b` + `.stat .l small{display:block}` in
design-system/css/ed-blackbox.css) then renders the bold name on the first line with the
descriptor on its own left-aligned line below.

Only `<div class="l">NAME<small>…</small>` tiles are touched — dossier headline tiles put
their <small> inside `.n` (the "/100"), not `.l`, so they don't match. Idempotent (a name
already wrapped in <b> is skipped).

Read-only elsewhere; rewrites guides/ships/by-role/*.html. Run from anywhere.

Usage:
  python3 scripts/bold-roster-stat-labels.py --dry-run
  python3 scripts/bold-roster-stat-labels.py
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BY_ROLE = REPO / "guides" / "ships" / "by-role"
# capture the label text (no tags) immediately followed by <small>
PAT = re.compile(r'(<div class="l">)(?!<b>)([^<]+?)(<small>)')


def main(argv):
    dry = "--dry-run" in argv
    files = changed = 0
    for path in sorted(BY_ROLE.glob("*.html")):
        html = path.read_text(encoding="utf-8")
        n = len(PAT.findall(html))
        if not n:
            continue
        new = PAT.sub(lambda m: f'{m.group(1)}<b>{m.group(2).strip()}</b>{m.group(3)}', html)
        if new != html:
            files += 1
            changed += n
            if not dry:
                path.write_text(new, encoding="utf-8")
            print(f"  {'(dry) ' if dry else ''}{path.relative_to(REPO)}  {n} tile(s)")
    verb = "would update" if dry else "updated"
    print(f"done — {verb} {changed} roster tile(s) across {files} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
