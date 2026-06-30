#!/usr/bin/env python3
"""
color-class-pills.py — colour-code ship pad-class tags.

The ship **pad-class** tag is rendered as `<span class="pill neutral">Large|Medium|Small
</span>` (the Class column on by-role ladders + the rating-methodology ship table). This
script swaps the neutral pill for a class-coloured one so the pad class reads at a glance:

  Large  -> pill pad-large   (red)
  Medium -> pill pad-medium  (amber / yellow)
  Small  -> pill pad-small   (green)

The colours live in design-system/css/ed-blackbox.css (`.pill.pad-*`).

It handles two markup forms:
  1. `class="pill neutral">(Large|Medium|Small)<`  — the full-ladder Class pills.
  2. a plain `<td>(Large|Medium|Small)</td>` Class cell that immediately follows the row's
     `<td class="mod">…</td>` ship cell — the by-role per-class tables (§04/05/06) and the
     dossier "How It Compares" peer tables, where the Class column was plain text. The cell
     is wrapped: `<td><span class="pill pad-…">Class</span></td>`.

SCOPE: form 2 only matches a bare class cell sitting right after a `<td class="mod">` cell,
so non-class `<td>Medium</td>`-style cells can't be hit. The amber `pill md">Medium` tags on
systems/activities pages mean *difficulty/payout*, NOT pad class, and are left untouched.
Idempotent (already-coloured pills/cells don't re-match).

Read-only elsewhere; rewrites guides/**/*.html. Run from anywhere.

Usage:
  python3 scripts/color-class-pills.py --dry-run
  python3 scripts/color-class-pills.py
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUIDES = REPO / "guides"
CLASS_TO_MOD = {"Large": "pad-large", "Medium": "pad-medium", "Small": "pad-small"}
# form 1: full-ladder neutral pills
PAT = re.compile(r'class="pill neutral">(Large|Medium|Small)<')
# form 2: a bare full-word Class cell right after the row's ship (mod) cell
CELL = re.compile(r'(<td class="mod">(?:(?!</td>).)*?</td>\s*)<td>(Large|Medium|Small)</td>', re.S)
# form 3: an abbreviated Class cell (S/M/L) right after the mod cell (combat per-class tables);
# expanded to the full word for consistency with every other table.
ABBR = re.compile(r'(<td class="mod">(?:(?!</td>).)*?</td>\s*)<td>([SML])</td>', re.S)
ABBR_MAP = {"S": ("pad-small", "Small"), "M": ("pad-medium", "Medium"), "L": ("pad-large", "Large")}


def convert(html):
    """Apply all three forms; return (new_html, n_changed)."""
    n = [0]
    def repl_pill(m):
        n[0] += 1
        return f'class="pill {CLASS_TO_MOD[m.group(1)]}">{m.group(1)}<'
    def repl_cell(m):
        n[0] += 1
        return f'{m.group(1)}<td><span class="pill {CLASS_TO_MOD[m.group(2)]}">{m.group(2)}</span></td>'
    def repl_abbr(m):
        n[0] += 1
        pad, word = ABBR_MAP[m.group(2)]
        return f'{m.group(1)}<td><span class="pill {pad}">{word}</span></td>'
    html = PAT.sub(repl_pill, html)
    html = CELL.sub(repl_cell, html)
    html = ABBR.sub(repl_abbr, html)
    return html, n[0]


def main(argv):
    dry = "--dry-run" in argv
    files = changed = 0
    for path in sorted(GUIDES.rglob("*.html")):
        html = path.read_text(encoding="utf-8")
        new, n = convert(html)
        if n and new != html:
            files += 1
            changed += n
            if not dry:
                path.write_text(new, encoding="utf-8")
            print(f"  {'(dry) ' if dry else ''}{path.relative_to(REPO)}  {n} tag(s)")
    verb = "would colour" if dry else "coloured"
    print(f"done — {verb} {changed} pad-class tag(s) across {files} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
