#!/usr/bin/env python3
"""
sort-byrole-ladders.py — re-sort the by-role page tables by rating, descending.

`reconcile-ratings-html.py` only re-sorts a ranking table when it ALSO updates or
drops a row in that table (its resort is gated on a change). When rows are *appended*
to a table with already-canonical ratings — e.g. when new dossier'd hulls are added
to a by-role ladder — reconcile makes no value change, so the resort never fires and
the new rows sit at the bottom out of order. This script closes that gap.

For each guides/ships/by-role/<role>.html it sorts the rows of:
  * every RANKING table (one carrying <span class="rscore">N</span>) by N, descending;
  * every COST table (a <table> with <td class="mod"> ship names but NO rscore) by the
    ship's canonical rating from data/ship-ratings/<role>.json, descending — so the cost
    table order mirrors its ranking table. A non-ranking table is only reordered when
    EVERY row's ship resolves to a canonical rating; this guards the §08 engineering
    table (its <td class="mod"> holds module names, not ships) from being touched.

Sorting is stable, so ties keep their authored order. Read-only on data/; rewrites only
by-role HTML. Idempotent. Run from anywhere.

Usage:
  python3 scripts/sort-byrole-ladders.py --dry-run      # preview
  python3 scripts/sort-byrole-ladders.py                # apply, all roles
  python3 scripts/sort-byrole-ladders.py trading ax     # selected roles
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BY_ROLE = REPO / "guides" / "ships" / "by-role"
DATA = REPO / "data" / "ship-ratings"
ROLES = ["ax", "combat", "exploration", "mining", "multipurpose", "passenger", "trading"]

TAG_RE = re.compile(r"<[^>]+>")
TABLE_RE = re.compile(r"<table\b[^>]*>.*?</table>", re.S | re.I)
TBODY_RE = re.compile(r"(<tbody>)(\s*)(.*?)(\s*)(</tbody>)", re.S | re.I)
ROW_RE = re.compile(r"[ \t]*<tr\b.*?</tr>", re.S | re.I)
MOD_RE = re.compile(r'<td class="mod">(.*?)</td>', re.S | re.I)
RSCORE_VAL_RE = re.compile(r'<span class="rscore">(\d+)</span>')


def norm_ship(raw: str) -> str:
    txt = TAG_RE.sub(" ", raw).replace("&mdash;", " ").replace("(baseline)", " ")
    txt = re.sub(r"\bthis hull\b", " ", txt, flags=re.I)
    txt = re.sub(r"\bthis\b", " ", txt, flags=re.I)
    txt = re.sub(r"[^a-z0-9]+", " ", txt.lower()).strip()
    return re.sub(r"\s+", " ", txt)


def load_canonical(role):
    doc = json.loads((DATA / f"{role}.json").read_text(encoding="utf-8"))
    return {norm_ship(r["ship"]): r["rating"] for r in doc["ratings"]}


def sort_table(table_html, canon):
    """Return (new_table_html, changed). Ranking tables sort by rscore; cost tables
    sort by canonical rating, but ONLY if every row resolves to a known ship."""
    m = TBODY_RE.search(table_html)
    if not m:
        return table_html, False
    open_tag, lead_ws, body, trail_ws, close_tag = m.groups()
    rows = ROW_RE.findall(body)
    if len(rows) < 2:
        return table_html, False

    is_rank = bool(RSCORE_VAL_RE.search(table_html))
    keyed = []
    for i, row in enumerate(rows):
        if is_rank:
            mv = RSCORE_VAL_RE.search(row)
            key = int(mv.group(1)) if mv else -1
        else:
            mm = MOD_RE.search(row)
            ship = norm_ship(mm.group(1)) if mm else None
            if ship not in canon:
                return table_html, False  # not a sortable ship table (e.g. engineering)
            key = canon[ship]
        keyed.append((key, i, row))

    order = sorted(keyed, key=lambda t: (-t[0], t[1]))  # rating desc, stable
    if [t[1] for t in order] == list(range(len(rows))):
        return table_html, False  # already sorted

    new_body = "\n".join(r for _, _, r in order)
    new_tbody = f"{open_tag}{lead_ws}{new_body}{trail_ws}{close_tag}"
    return table_html[:m.start()] + new_tbody + table_html[m.end():], True


def process(path, canon, dry):
    html = path.read_text(encoding="utf-8")
    out, last, n = [], 0, 0
    for tm in TABLE_RE.finditer(html):
        new_t, changed = sort_table(tm.group(0), canon)
        if changed:
            out.append(html[last:tm.start()])
            out.append(new_t)
            last = tm.end()
            n += 1
    out.append(html[last:])
    new_html = "".join(out)
    if n and not dry:
        path.write_text(new_html, encoding="utf-8")
    return n


def main(argv):
    dry = "--dry-run" in argv
    roles = [a for a in argv if a in ROLES] or ROLES
    grand_t = grand_f = 0
    for role in roles:
        bp = BY_ROLE / f"{role}.html"
        if not bp.exists():
            continue
        n = process(bp, load_canonical(role), dry)
        if n:
            grand_f += 1
            grand_t += n
            print(f"  {'(dry) ' if dry else ''}{bp.name:<22} sorted {n} table(s)")
    verb = "would sort" if dry else "sorted"
    print(f"done — {verb} {grand_t} table(s) across {grand_f} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
