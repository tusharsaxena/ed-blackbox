#!/usr/bin/env python3
"""sort-compare-tables.py — sort "How It Compares" tables by rating, descending.

Every ship page (dossiers/ + by-role/) carries one or more `table.cmp` comparison
tables whose last column is a numeric rating in `<span class="rscore">NN</span>`
(plus a `.bar mini` width hint). This rewrites each such table's <tbody> so its
<tr> rows are ordered by that rating, highest first.

Rules:
  - Rows are sorted by their `.rscore` integer, DESCENDING.
  - A dash rating (`<span class="rscore">&mdash;</span>`, i.e. "not rated") sorts LAST.
  - Ties keep their original relative order (stable sort) — this preserves the
    intended ordering of equally-rated ships (incl. the "this hull" baseline row,
    which is sorted by its own rating like any other row).
  - Only `<table class="cmp">` tables are touched; `table.l3` / `table.data` etc.
    are left alone. Row markup, indentation, and the rating bar are preserved
    verbatim — rows are only reordered, never rewritten.

Idempotent: re-running on already-sorted tables changes nothing.

Usage:
  python3 scripts/sort-compare-tables.py            # rewrite all ship pages in place
  python3 scripts/sort-compare-tables.py --check     # report what WOULD change, write nothing
"""

import re
import sys
from pathlib import Path

# Resolve target dirs relative to this script so it runs from anywhere.
ROOT = Path(__file__).resolve().parent.parent
TARGET_DIRS = [ROOT / "guides" / "ships" / "dossiers",
               ROOT / "guides" / "ships" / "by-role"]

TABLE_RE = re.compile(r'(<table class="cmp">.*?</table>)', re.DOTALL)
TBODY_RE = re.compile(r'(<tbody>)(.*?)(</tbody>)', re.DOTALL)
ROW_RE = re.compile(r'\s*<tr\b.*?</tr>', re.DOTALL)
RSCORE_RE = re.compile(r'class="rscore">\s*(.*?)\s*<')

# Dash / non-numeric ratings sort last. Use a sentinel below any real score.
NOT_RATED = -1


def row_rating(row):
    m = RSCORE_RE.search(row)
    if not m:
        return NOT_RATED
    val = m.group(1)
    try:
        return int(val)
    except ValueError:
        return NOT_RATED  # &mdash; or any non-numeric


def sort_tbody(match):
    head, inner, tail = match.group(1), match.group(2), match.group(3)
    rows = ROW_RE.findall(inner)
    if not rows:
        return match.group(0)
    # Preserve any whitespace outside the row span (after <tbody>, before </tbody>).
    start = inner.index(rows[0])
    end = inner.rindex(rows[-1]) + len(rows[-1])
    prefix, suffix = inner[:start], inner[end:]
    # Stable descending sort; dash (NOT_RATED) lands last because -(-1)=1 > -(any score).
    ordered = sorted(rows, key=lambda r: -row_rating(r))
    return head + prefix + "".join(ordered) + suffix + tail


def sort_tables(html):
    def repl(m):
        return TBODY_RE.sub(sort_tbody, m.group(1))
    return TABLE_RE.sub(repl, html)


def main():
    check = "--check" in sys.argv
    files = sorted(f for d in TARGET_DIRS for f in d.glob("*.html"))
    changed = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        updated = sort_tables(original)
        if updated != original:
            changed += 1
            if check:
                print(f"would sort: {f.relative_to(ROOT)}")
            else:
                f.write_text(updated, encoding="utf-8")
                print(f"sorted: {f.relative_to(ROOT)}")
    verb = "would change" if check else "changed"
    print(f"\n{len(files)} ship pages scanned, {changed} {verb}.")


if __name__ == "__main__":
    main()
