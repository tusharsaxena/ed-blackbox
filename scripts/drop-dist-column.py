#!/usr/bin/env python3
"""
drop-dist-column.py — remove the "Dist." (power-distributor class, PDn) column
from the full-ladder ranking table in guides/ships/by-role/*.html and rebalance
the remaining five columns to fill 100% width.

Why: the Dist. column (values like PD7) showed each hull's max power-distributor
core-slot class. It was judged not relevant to the role rankings and dropped.

Scope / safety: the edit targets ONLY the 6-column full-ladder table, identified
by three signatures that appear nowhere else in these pages:
  1. the colgroup "17/10/16/7/38/12" — the 7% width is unique to this table
  2. the header cell  <th class="num">Dist.</th>  (exactly one per file)
  3. the body cells    <td class="num">PD[0-9]</td>  (PDn never appears elsewhere;
     the cost tables also use class="num" but hold credit values, never PDn)
The per-class and cost tables (which legitimately use class="num") are untouched.

Rebalance: the freed 7% goes to the cramped one-line-verdict column:
  17 / 10 / 16 / 7(Dist) / 38(verdict) / 12   ->   17 / 10 / 16 / 45(verdict) / 12

Idempotent: running again on an already-processed file changes nothing (it reports
0 edits). Pass file paths as args, or none to default to all by-role pages.

Usage:
  python3 scripts/drop-dist-column.py [file ...]
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BY_ROLE = REPO / "guides" / "ships" / "by-role"

OLD_COLGROUP = (
    '<colgroup><col style="width:17%"><col style="width:10%">'
    '<col style="width:16%"><col style="width:7%">'
    '<col style="width:38%"><col style="width:12%"></colgroup>'
)
NEW_COLGROUP = (
    '<colgroup><col style="width:17%"><col style="width:10%">'
    '<col style="width:16%"><col style="width:45%">'
    '<col style="width:12%"></colgroup>'
)
DIST_HEADER = '<th class="num">Dist.</th>'
PD_CELL_RE = re.compile(r'<td class="num">PD[0-9]+</td>')


def process(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    before = text

    n_colgroup = text.count(OLD_COLGROUP)
    text = text.replace(OLD_COLGROUP, NEW_COLGROUP)

    n_header = text.count(DIST_HEADER)
    text = text.replace(DIST_HEADER, "")

    n_cells = len(PD_CELL_RE.findall(text))
    text = PD_CELL_RE.sub("", text)

    changed = text != before
    if changed:
        path.write_text(text, encoding="utf-8")

    return {
        "file": path.name,
        "colgroups": n_colgroup,
        "headers": n_header,
        "cells": n_cells,
        "changed": changed,
    }


def main(argv):
    if argv:
        targets = [Path(a) for a in argv]
    else:
        targets = sorted(BY_ROLE.glob("*.html"))

    if not targets:
        print("no target files found", file=sys.stderr)
        return 1

    total = 0
    for path in targets:
        if not path.exists():
            print(f"  ! {path} not found", file=sys.stderr)
            continue
        r = process(path)
        total += r["cells"]
        flag = "edited " if r["changed"] else "no-op  "
        print(
            f"  {flag} {r['file']:<22} "
            f"colgroup:{r['colgroups']} header:{r['headers']} PDn-cells:{r['cells']}"
        )
    print(f"done — {total} PDn cells removed across {len(targets)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
