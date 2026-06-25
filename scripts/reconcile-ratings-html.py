#!/usr/bin/env python3
"""
reconcile-ratings-html.py — push the canonical ship ratings into the HTML guides.

Source of truth: data/ship-ratings/<role>.json (built by compute-ship-ratings.py).
This script makes the guides match those files:

  By-role pages  guides/ships/by-role/<role>.html
    - every ranking table (full-ladder + per-class breakdowns; the tables that carry
      <span class="rscore">):
        * a ship present in the data file  -> its rscore and the row's --pct bar are
          set to the canonical value;
        * a ship ABSENT from the data file (a dropped tier-2 hull) -> the row is removed;
        * remaining rows are RE-SORTED by rating, descending.
    - cost tables (no rscore): rows for a DROPPED tier-2 hull (one listed in the data
      file's `excluded_no_dossier_conflict`) are removed too, so the page doesn't keep
      pricing a hull it no longer ranks. Engineering tables (module rows) are untouched
      — their ship column holds module names, never ship names, so nothing matches.

  NOTE: removing a tier-2 hull only clears its table rows. Prose that names it
  (section intros, callouts, pick cards, stat grids) and any subsection emptied by the
  removal still need an editorial pass — this script reports emptied tbodies so that
  pass knows where to look.

  Dossier pages  guides/ships/dossiers/<ship>-<role>.html
    - the "How It Compares" peer tables (<table class="cmp">): a peer present in the
      data file has its value reconciled; a peer ABSENT from the data file (dropped
      tier-2 hull) has its row removed. Peer tables keep their authored order.

Idempotent: a second run makes no changes. Use --dry-run to preview.

Usage:
  python3 scripts/reconcile-ratings-html.py --dry-run        # preview all roles
  python3 scripts/reconcile-ratings-html.py                  # apply, all roles
  python3 scripts/reconcile-ratings-html.py trading ax       # selected roles
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BY_ROLE = REPO / "guides" / "ships" / "by-role"
DOSSIERS = REPO / "guides" / "ships" / "dossiers"
DATA = REPO / "data" / "ship-ratings"
ROLES = ["ax", "combat", "exploration", "mining", "multipurpose", "passenger", "trading"]

TAG_RE = re.compile(r"<[^>]+>")
TABLE_RE = re.compile(r"<table\b[^>]*>.*?</table>", re.S | re.I)
TBODY_RE = re.compile(r"(<tbody>)(\s*)(.*?)(\s*)(</tbody>)", re.S | re.I)
ROW_RE = re.compile(r"[ \t]*<tr\b.*?</tr>", re.S | re.I)
MOD_RE = re.compile(r'<td class="mod">(.*?)</td>', re.S | re.I)
RSCORE_RE = re.compile(r'(<span class="rscore">)\d+(</span>)')
RSCORE_VAL_RE = re.compile(r'<span class="rscore">(\d+)</span>')
PCT_RE = re.compile(r"(--pct:)\d+")


def norm_ship(raw: str) -> str:
    txt = TAG_RE.sub(" ", raw).replace("&mdash;", " ").replace("(baseline)", " ")
    txt = re.sub(r"\bthis hull\b", " ", txt, flags=re.I)
    txt = re.sub(r"\bthis\b", " ", txt, flags=re.I)
    txt = re.sub(r"[^a-z0-9]+", " ", txt.lower()).strip()
    return re.sub(r"\s+", " ", txt)


def load_canonical(role):
    doc = json.loads((DATA / f"{role}.json").read_text(encoding="utf-8"))
    canon = {norm_ship(r["ship"]): r["rating"] for r in doc["ratings"]}
    excluded = {norm_ship(e["ship"]) for e in doc.get("excluded_no_dossier_conflict", [])}
    return canon, excluded


def reconcile_table(table_html, canon, excluded, resort):
    """Return (new_table_html, n_updated, n_dropped, emptied).
    Ranking tables (carry rscore): canonical ships have value+pct reconciled, ships
    not in canon are dropped, and rows are optionally re-sorted by rating desc.
    Non-ranking tables (e.g. cost): only rows naming an EXCLUDED tier-2 hull are
    dropped; everything else (incl. module/engineering rows) is left untouched."""
    is_rank = bool(RSCORE_VAL_RE.search(table_html))
    m = TBODY_RE.search(table_html)
    if not m:
        return table_html, 0, 0, False
    open_tag, lead_ws, body, trail_ws, close_tag = m.groups()

    rows = ROW_RE.findall(body)
    updated = dropped = 0
    kept = []  # (sort_value_or_None, row_text)
    for row in rows:
        m_mod = MOD_RE.search(row)
        m_val = RSCORE_VAL_RE.search(row)
        ship = norm_ship(m_mod.group(1)) if m_mod else None

        if is_rank:
            if not (m_mod and m_val):
                kept.append((None, row))            # defensive: keep odd rows
                continue
            if ship not in canon:
                dropped += 1                         # tier-2 / non-canonical -> drop
                continue
            target = canon[ship]
            if int(m_val.group(1)) != target:
                updated += 1
            row = RSCORE_RE.sub(rf"\g<1>{target}\g<2>", row)
            row = PCT_RE.sub(rf"\g<1>{target}", row)
            kept.append((target, row))
        else:
            if ship and ship in excluded:            # cost row for a dropped hull
                dropped += 1
                continue
            kept.append((None, row))

    if resort and is_rank:
        kept.sort(key=lambda kv: (-(kv[0] if kv[0] is not None else -1)))

    new_body = "\n".join(r for _, r in kept)
    new_tbody = f"{open_tag}{lead_ws}{new_body}{trail_ws}{close_tag}"
    emptied = (len(rows) > 0 and len(kept) == 0)
    return table_html[:m.start()] + new_tbody + table_html[m.end():], updated, dropped, emptied


def reconcile_file(path, canon, excluded, kind, dry):
    """kind: 'by-role' processes all tables (rank + cost) and re-sorts ranking ones;
    'dossier' processes only ranking (cmp) tables and keeps their authored order."""
    html = path.read_text(encoding="utf-8")
    total_u = total_d = emptied = 0
    out, last = [], 0
    for tm in TABLE_RE.finditer(html):
        thtml = tm.group(0)
        if kind == "dossier" and not RSCORE_VAL_RE.search(thtml):
            continue  # never touch a dossier's non-ranking tables
        new_t, u, d, emp = reconcile_table(
            thtml, canon, excluded, resort=(kind == "by-role"))
        if u or d:
            out.append(html[last:tm.start()])
            out.append(new_t)
            last = tm.end()
            total_u += u
            total_d += d
            emptied += int(emp)
    out.append(html[last:])
    new_html = "".join(out)
    changed = new_html != html
    if changed and not dry:
        path.write_text(new_html, encoding="utf-8")
    return changed, total_u, total_d, emptied


def main(argv):
    dry = "--dry-run" in argv
    roles = [a for a in argv if a in ROLES] or ROLES
    grand_u = grand_d = grand_files = grand_emptied = 0
    for role in roles:
        canon, excluded = load_canonical(role)
        bp = BY_ROLE / f"{role}.html"
        if bp.exists():
            ch, u, d, emp = reconcile_file(bp, canon, excluded, "by-role", dry)
            if ch:
                grand_files += 1
                tag = f" EMPTIED:{emp}" if emp else ""
                print(f"  {'(dry) ' if dry else ''}{bp.name:<30} updated:{u} dropped:{d} resorted{tag}")
            grand_u += u; grand_d += d; grand_emptied += emp
        for dp in sorted(DOSSIERS.glob(f"*-{role}.html")):
            ch, u, d, emp = reconcile_file(dp, canon, excluded, "dossier", dry)
            if ch:
                grand_files += 1
                print(f"  {'(dry) ' if dry else ''}{dp.name:<30} updated:{u} dropped:{d}")
            grand_u += u; grand_d += d; grand_emptied += emp
    verb = "would change" if dry else "changed"
    print(f"done — {verb} {grand_files} file(s); {grand_u} ratings updated, {grand_d} rows dropped"
          + (f"; {grand_emptied} table(s) emptied (need editorial pass)" if grand_emptied else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
