#!/usr/bin/env python3
"""
fix-arx-table-corruption.py — repair per-character <td> corruption in ARX-section tables.

Five "ARX Pre-Built Option" spec tables were generated with their tbody corrupted: each
logical 2-cell row (label, value) was exploded into TWO rows, each split into one <td> per
character (e.g. <td>I</td><td>n</td><td>c</td>… spelling "Includes"). They render as garbled
single-character cells.

This finds the <table class="data"> inside <section id="section-arx-pre-built-option">,
concatenates each corrupted row's single-character cells back into a string, and pairs the
rows two-at-a-time into clean <tr><td>label</td><td>value</td></tr> rows.

Only acts on tables showing the corruption (a tbody row of 3+ consecutive single-char <td>).
Idempotent. NOTE: pure concatenation can't recover a <td> that was dropped entirely (one
table lost the space in "paint job"); fix such cases by hand afterwards.

Usage:
  python3 scripts/fix-arx-table-corruption.py --dry-run
  python3 scripts/fix-arx-table-corruption.py
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOSSIERS = REPO / "guides" / "ships" / "dossiers"
CORRUPT = re.compile(r"<td>[^<]</td><td>[^<]</td><td>[^<]</td>")
TR_RE = re.compile(r"<tr\b[^>]*>(.*?)</tr>", re.S)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
SECTION_RE = re.compile(r'<section id="section-arx-pre-built-option">.*?</section>', re.S)
TABLE_RE = re.compile(r'<table class="data">.*?</table>', re.S)


def rebuild_tbody(tbody):
    rows = TR_RE.findall(tbody)
    cells = ["".join(TD_RE.findall(r)) for r in rows]
    out = []
    for i in range(0, len(cells), 2):
        c1 = cells[i]
        c2 = cells[i + 1] if i + 1 < len(cells) else ""
        out.append(f"        <tr><td>{c1}</td><td>{c2}</td></tr>")
    return "<tbody>\n" + "\n".join(out) + "\n      </tbody>"


def fix_table(table):
    if not CORRUPT.search(table):
        return table, False
    m = re.search(r"<tbody>.*?</tbody>", table, re.S)
    if not m:
        return table, False
    return table[:m.start()] + rebuild_tbody(m.group(0)) + table[m.end():], True


def fix_section(html):
    changed = [False]
    def repl_section(ms):
        sec = ms.group(0)
        def repl_table(mt):
            new_t, ch = fix_table(mt.group(0))
            if ch:
                changed[0] = True
            return new_t
        return TABLE_RE.sub(repl_table, sec)
    new = SECTION_RE.sub(repl_section, html)
    return new, changed[0]


def main(argv):
    dry = "--dry-run" in argv
    n = 0
    for path in sorted(DOSSIERS.glob("*.html")):
        html = path.read_text(encoding="utf-8")
        if "section-arx-pre-built-option" not in html:
            continue
        new, changed = fix_section(html)
        if changed:
            n += 1
            if not dry:
                path.write_text(new, encoding="utf-8")
            print(f"  {'(dry) ' if dry else ''}{path.name}")
    print(f"done — {'would fix' if dry else 'fixed'} {n} corrupted ARX table(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
