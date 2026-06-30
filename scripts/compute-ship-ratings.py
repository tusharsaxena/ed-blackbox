#!/usr/bin/env python3
"""
compute-ship-ratings.py — build the canonical ship-rating data files.

Writes data/ship-ratings/<role>.json: the 1-100 suitability rating for every
ship in every role. These files are the **source of truth** for ship ratings;
the HTML guides (ship dossiers + by-role ladders) reconcile to them via
`reconcile-ratings-html.py`. Verify drift any time with
`audit-ratings-consistency.py`.

These ratings are *editorial judgement* (see guides/ships/rating-methodology.html),
NOT coriolis-data game stats — that is why they live outside data/ships|modules.

CANONICAL VALUE — resolution rules (per role, per ship):
  * Ship HAS a dossier (guides/ships/dossiers/<ship>-<role>.html):
      canonical = the dossier's HEADLINE rating (<div class="n">N<small>/100).
      The dossier is authoritative; any divergent by-role ladder value is stale.
  * Ship has NO dossier:
      - if every place it appears (by-role ladder + peer-comparison rows in other
        dossiers) agrees on one value -> that value (a consistent, dossier-less hull).
      - if those places DISAGREE (a "tier-2" conflict, e.g. passenger Anaconda) ->
        EXCLUDED. With no dossier to adjudicate, the rating is dropped entirely;
        reconcile-ratings-html.py then removes the ship from the ladder and the
        peer-comparison tables.

Read-only on the HTML. Writes data/ship-ratings/. Run from anywhere.

Usage:
  python3 scripts/compute-ship-ratings.py            # all roles
  python3 scripts/compute-ship-ratings.py trading    # selected roles
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BY_ROLE = REPO / "guides" / "ships" / "by-role"
DOSSIERS = REPO / "guides" / "ships" / "dossiers"
OUT = REPO / "data" / "ship-ratings"
ROLES = ["ax", "combat", "exploration", "mining", "multipurpose", "passenger", "trading"]

TAG_RE = re.compile(r"<[^>]+>")
ROW_RE = re.compile(r"<tr\b.*?</tr>", re.S | re.I)
MOD_RE = re.compile(r'<td class="mod">(.*?)</td>', re.S | re.I)
RSCORE_RE = re.compile(r'<span class="rscore">(\d+)</span>')
HEADLINE_RE = re.compile(r'<div class="n">(\d+)\s*<small>\s*/100')
SUBJECT_RE = re.compile(r'pill md">\s*this|class="base"|\(baseline\)', re.I)


def norm_ship(raw: str) -> str:
    txt = TAG_RE.sub(" ", raw).replace("&mdash;", " ").replace("(baseline)", " ")
    txt = re.sub(r"\bthis hull\b", " ", txt, flags=re.I)
    txt = re.sub(r"\bthis\b", " ", txt, flags=re.I)
    txt = re.sub(r"[^a-z0-9]+", " ", txt.lower()).strip()
    return re.sub(r"\s+", " ", txt)


def display_of(raw: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", raw)).strip()


def row_pairs(html: str):
    for row in ROW_RE.findall(html):
        m_mod, m_score = MOD_RE.search(row), RSCORE_RE.search(row)
        if m_mod and m_score:
            ship = norm_ship(m_mod.group(1))
            if ship:
                yield ship, display_of(m_mod.group(1)), int(m_score.group(1))


def compute_role(role: str):
    # gather all assertions
    values = defaultdict(set)        # norm -> {int}
    display = {}                     # norm -> best display name
    dossier_of = {}                  # norm -> (filename, headline_value)

    def remember(norm, disp):
        # prefer a display without trailing markers; first non-empty wins, by-role preferred
        if norm not in display or (len(disp) < len(display[norm]) and disp):
            display[norm] = disp

    # by-role ladder + per-class tables
    bypage = BY_ROLE / f"{role}.html"
    if bypage.exists():
        for norm, disp, val in row_pairs(bypage.read_text(encoding="utf-8")):
            values[norm].add(val)
            remember(norm, disp)

    # dossiers of this role
    for dpath in sorted(DOSSIERS.glob(f"*-{role}.html")):
        html = dpath.read_text(encoding="utf-8")
        # subject + headline
        m_head = HEADLINE_RE.search(html)
        subj_norm = subj_disp = None
        for row in ROW_RE.findall(html):
            if SUBJECT_RE.search(row):
                m_mod = MOD_RE.search(row)
                if m_mod:
                    subj_norm, subj_disp = norm_ship(m_mod.group(1)), display_of(m_mod.group(1))
                break
        if m_head and subj_norm:
            hv = int(m_head.group(1))
            dossier_of[subj_norm] = (dpath.name, hv)
            values[subj_norm].add(hv)
            remember(subj_norm, subj_disp)
        # peer rows
        for norm, disp, val in row_pairs(html):
            values[norm].add(val)
            remember(norm, disp)

    # resolve canonical
    ratings, excluded = [], []
    for norm in sorted(values):
        if norm in dossier_of:
            fname, hv = dossier_of[norm]
            ratings.append({"ship": display[norm], "rating": hv, "dossier": fname})
        else:
            vals = values[norm]
            if len(vals) == 1:
                ratings.append({"ship": display[norm], "rating": next(iter(vals)), "dossier": None})
            else:
                excluded.append({"ship": display[norm], "values": sorted(vals)})

    ratings.sort(key=lambda r: (-r["rating"], r["ship"]))
    return ratings, excluded


def main(argv):
    roles = [a for a in argv if a in ROLES] or ROLES
    OUT.mkdir(parents=True, exist_ok=True)
    grand = 0
    for role in roles:
        ratings, excluded = compute_role(role)
        # Preserve authored SCORECARD data across rebuilds. The rating-rationale
        # scorecard (per-role factor weights + each ship's factor breakdown) is
        # authored editorial data that lives in these files but is NOT derived
        # from the dossier HTML, so a from-scratch rebuild must carry it over.
        # scorecard_weights -> top-level; each ship's `scorecard` -> by ship name.
        prev = {}
        prev_path = OUT / f"{role}.json"
        if prev_path.exists():
            prev = json.loads(prev_path.read_text(encoding="utf-8"))
        prev_cards = {r["ship"]: r["scorecard"]
                      for r in prev.get("ratings", []) if r.get("scorecard")}
        for r in ratings:
            if r["ship"] in prev_cards:
                r["scorecard"] = prev_cards[r["ship"]]
        doc = {
            "role": role,
            "_comment": ("Canonical 1-100 suitability ratings for this role — the SOURCE OF "
                         "TRUTH. HTML (dossier headlines + by-role ladders + peer tables) must "
                         "match. Editorial judgement, not coriolis game data. "
                         "Rebuild: scripts/compute-ship-ratings.py · "
                         "push to HTML: scripts/reconcile-ratings-html.py · "
                         "verify: scripts/audit-ratings-consistency.py"),
        }
        if prev.get("scorecard_weights"):
            doc["scorecard_weights"] = prev["scorecard_weights"]
        doc["count"] = len(ratings)
        doc["ratings"] = ratings
        if excluded:
            doc["excluded_no_dossier_conflict"] = excluded
        (OUT / f"{role}.json").write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        grand += len(ratings)
        exc = f"  (excluded {len(excluded)}: {', '.join(e['ship'] for e in excluded)})" if excluded else ""
        print(f"  {role:<13} {len(ratings):>3} ships{exc}")
    print(f"done — {grand} ratings across {len(roles)} role file(s) in {OUT.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
