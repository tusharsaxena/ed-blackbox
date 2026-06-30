#!/usr/bin/env python3
"""
audit-ratings-consistency.py — cross-page audit of ship suitability ratings.

Every (role, ship) 1-100 rating is asserted in several places that must all agree:

  * guides/ships/best-ships-by-role/<role>.html
      - the full-ladder ranking table
      - the per-class breakdown tables
        (both: <td class="mod">SHIP…</td> … <span class="rscore">N</span>)
  * guides/ships/ship-dossiers/<ship>-<role>.html
      - the headline rating  <div class="n">N<small>/100</small>
      - the subject row in its peer table (marked `pill md">this` / baseline)
      - every peer-comparison row  <td class="mod">SHIP…</td> … rscore">N

This script collects every assertion, groups them by (role, normalised ship),
and flags any group whose asserted values are not unanimous — with full
provenance (file + the distinct values) for each mismatch.

Read-only. Exit status: 0 if fully consistent, 1 if any mismatch is found.

Usage:
  python3 scripts/audit-ratings-consistency.py            # all roles
  python3 scripts/audit-ratings-consistency.py combat     # one or more roles
  python3 scripts/audit-ratings-consistency.py --json      # machine-readable
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BY_ROLE = REPO / "guides" / "ships" / "best-ships-by-role"
DOSSIERS = REPO / "guides" / "ships" / "ship-dossiers"
ROLES = ["ax", "combat", "exploration", "mining", "multipurpose", "passenger", "trading"]

TAG_RE = re.compile(r"<[^>]+>")
ROW_RE = re.compile(r"<tr\b.*?</tr>", re.S | re.I)
MOD_RE = re.compile(r'<td class="mod">(.*?)</td>', re.S | re.I)
RSCORE_RE = re.compile(r'<span class="rscore">(\d+)</span>')
HEADLINE_RE = re.compile(r'<div class="n">(\d+)\s*<small>\s*/100')


def norm_ship(raw: str) -> str:
    """Strip tags/markers and normalise a ship display name for grouping."""
    txt = TAG_RE.sub(" ", raw)
    txt = txt.replace("&mdash;", " ").replace("(baseline)", " ")
    txt = re.sub(r"\bthis hull\b", " ", txt, flags=re.I)
    txt = re.sub(r"\bthis\b", " ", txt, flags=re.I)
    txt = re.sub(r"[^a-z0-9]+", " ", txt.lower()).strip()
    txt = re.sub(r"\s+", " ", txt)
    return txt


def row_assertions(html: str):
    """Yield (normalised_ship, display, rating) for every table row that pairs a
    ship name (<td class="mod">) with an rscore."""
    for row in ROW_RE.findall(html):
        m_mod = MOD_RE.search(row)
        m_score = RSCORE_RE.search(row)
        if not (m_mod and m_score):
            continue
        display = re.sub(r"\s+", " ", TAG_RE.sub(" ", m_mod.group(1))).strip()
        ship = norm_ship(m_mod.group(1))
        if not ship:
            continue
        yield ship, display, int(m_score.group(1))


def audit(roles):
    # assertions[(role, ship)] = list of dicts {value, source, file, display}
    assertions = defaultdict(list)
    files_scanned = 0

    for role in roles:
        # --- by-role page (full-ladder + per-class tables) ---
        bypage = BY_ROLE / f"{role}.html"
        if bypage.exists():
            files_scanned += 1
            html = bypage.read_text(encoding="utf-8")
            for ship, display, val in row_assertions(html):
                assertions[(role, ship)].append(
                    {"value": val, "source": "by-role table", "file": bypage.name, "display": display}
                )

        # --- every dossier of this role ---
        for dpath in sorted(DOSSIERS.glob(f"*-{role}.html")):
            if dpath.name.endswith("-anchors.md"):
                continue
            files_scanned += 1
            html = dpath.read_text(encoding="utf-8")

            # headline rating -> attributed to the subject ship (the peer row marked `this`)
            m_head = HEADLINE_RE.search(html)
            subject = None
            for row in ROW_RE.findall(html):
                if re.search(r'pill md">\s*this|class="base"|\(baseline\)', row, re.I):
                    m_mod = MOD_RE.search(row)
                    if m_mod:
                        subject = (norm_ship(m_mod.group(1)),
                                   re.sub(r"\s+", " ", TAG_RE.sub(" ", m_mod.group(1))).strip())
                    break
            if m_head and subject:
                assertions[(role, subject[0])].append(
                    {"value": int(m_head.group(1)), "source": "dossier headline",
                     "file": dpath.name, "display": subject[1]}
                )

            # every peer-comparison row
            for ship, display, val in row_assertions(html):
                assertions[(role, ship)].append(
                    {"value": val, "source": "dossier peer table", "file": dpath.name, "display": display}
                )

    # find mismatches
    mismatches = []
    consistent = 0
    for (role, ship), items in sorted(assertions.items()):
        distinct = sorted({it["value"] for it in items})
        if len(distinct) > 1:
            # A ship "owns" a dossier for this role iff a headline rating was
            # attributed to it. Headline-backed conflicts (tier 1) have a clear
            # source of truth (the ship's own page); peer-only conflicts (tier 2)
            # are just cross-references in OTHER ships' dossiers — ambiguous.
            has_own_dossier = any(it["source"] == "dossier headline" for it in items)
            headline = next((it["value"] for it in items if it["source"] == "dossier headline"), None)
            mismatches.append({
                "role": role,
                "ship": next(it["display"] for it in items),
                "distinct": distinct,
                "has_own_dossier": has_own_dossier,
                "tier": 1 if has_own_dossier else 2,
                "headline": headline,
                "assertions": [
                    {"value": it["value"], "source": it["source"], "file": it["file"]}
                    for it in sorted(items, key=lambda x: (x["value"], x["file"]))
                ],
            })
        else:
            consistent += 1

    return {
        "roles": roles,
        "files_scanned": files_scanned,
        "ship_role_pairs": len(assertions),
        "consistent": consistent,
        "mismatches": mismatches,
    }


def main(argv):
    as_json = "--json" in argv
    roles = [a for a in argv if a in ROLES] or ROLES
    rpt = audit(roles)

    if as_json:
        print(json.dumps(rpt, indent=2))
        return 1 if rpt["mismatches"] else 0

    print(f"Scanned {rpt['files_scanned']} files across roles: {', '.join(roles)}")
    print(f"(role, ship) rating groups: {rpt['ship_role_pairs']}  |  consistent: {rpt['consistent']}  |  mismatches: {len(rpt['mismatches'])}")
    if not rpt["mismatches"]:
        print("\n✓ All ratings are consistent across dossiers and by-role pages.")
        return 0
    t1 = [m for m in rpt["mismatches"] if m["tier"] == 1]
    t2 = [m for m in rpt["mismatches"] if m["tier"] == 2]

    print(f"\n✗ MISMATCHES — tier 1 (ship has own dossier; headline is source of truth): {len(t1)}")
    for m in t1:
        print(f"\n  [{m['role']}] {m['ship']} — values differ: {m['distinct']}  (headline={m['headline']})")
        for a in m["assertions"]:
            print(f"      {a['value']:>3}  {a['source']:<20} {a['file']}")

    print(f"\n✗ MISMATCHES — tier 2 (NO own dossier; by-role ladder vs peer cross-refs — AMBIGUOUS): {len(t2)}")
    for m in t2:
        print(f"\n  [{m['role']}] {m['ship']} — values differ: {m['distinct']}  (no dedicated dossier)")
        for a in m["assertions"]:
            print(f"      {a['value']:>3}  {a['source']:<20} {a['file']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
