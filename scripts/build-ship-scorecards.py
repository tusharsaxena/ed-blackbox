#!/usr/bin/env python3
"""
build-ship-scorecards.py — inject the "Why This Rating" scorecard section into ship dossiers.

Source of truth: data/ship-ratings/<role>.json
  * scorecard_weights : the role's priority-ordered factors, each with an integer weight
                        (multiple of 5, summing to 100).
  * ratings[].scorecard : {verdict, factors:[{factor, earned, why}]} for a ship; earned
                        points sum to the ship's canonical rating.

For each ship that has a scorecard + a dossier, this renders a new
`<section id="section-why-this-rating">` (the approved Variant-A table) and places it
immediately BEFORE `<section id="section-how-it-compares">`. The styling lives in the
design system (table.data.scorecard); no per-page CSS is added.

Idempotent:
  * first run  -> INSERT the section, renumber every later .sec-num, insert the quick-nav
                  qn-item and bump every later qn-side. (Section ids are slug-based, so no
                  cross-page anchor breaks; only the displayed numbers shift.)
  * re-run     -> REPLACE the existing section in place (keeps its number + qn-item).

After a first-time insert anywhere, re-run scripts/generate-anchor-files.sh to refresh the
per-page <basename>-anchors.md catalogs.

Read-only on the data. Writes guides/ships/ship-dossiers/*.html. Run from anywhere.

Usage:
  python3 scripts/build-ship-scorecards.py            # all dossiers with scorecard data
  python3 scripts/build-ship-scorecards.py corvette   # only matching dossier basenames
  python3 scripts/build-ship-scorecards.py --check     # report, write nothing
"""
import html as html_lib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "ship-ratings"
DOSSIERS = REPO / "guides" / "ships" / "ship-dossiers"
ROLES = ["ax", "combat", "exploration", "mining", "multipurpose", "passenger", "trading"]

ROLE_LABEL = {
    "ax": "anti-Xeno", "combat": "combat", "exploration": "exploration",
    "mining": "mining", "multipurpose": "multipurpose", "passenger": "passenger",
    "trading": "trading",
}
ANCHOR = "section-why-this-rating"
TARGET = "section-how-it-compares"


def esc(s: str) -> str:
    return html_lib.escape(s, quote=False)


def build_section(num: int, role: str, rating: int, weights: dict, sc: dict) -> str:
    rows = []
    for f in sc["factors"]:
        name, earned = f["factor"], f["earned"]
        w = weights[name]
        pct = round(earned / w * 100)
        rows.append(
            f'      <tr><td class="fct">{esc(name)}</td>'
            f'<td class="sc"><span class="scval">{earned}</span><span class="den">/{w}</span>'
            f'<div class="bar mini"><i style="--pct:{pct}"></i></div></td>'
            f'<td class="wcell">{esc(f["why"])}</td></tr>'
        )
    total = (
        f'      <tr class="totalrow"><td class="fct"><b>Weighted total</b></td>'
        f'<td class="sc"><span class="scval">{rating}</span><span class="den">/100</span>'
        f'<div class="bar mini"><i style="--pct:{rating}"></i></div></td>'
        f'<td class="wcell"><em>Matches the headline suitability rating for this ship '
        f'in this role.</em></td></tr>'
    )
    return f"""  <!-- Why This Rating -->
  <section id="{ANCHOR}">
    <div class="sec-head"><span class="sec-num">{num:02d}</span><h2>Why This Rating</h2><span class="tag">Scorecard</span></div>
    <p class="lead">{esc(sc["verdict"])}</p>
    <p>The <b>{rating}/100</b> headline is a verdict against the {ROLE_LABEL[role]} role's priority-ordered factors. Each factor carries a <b>weight</b> (its share of 100); this hull earns part of each based on how it performs against the whole field. The points <b>sum to the rating</b>.</p>
    <div class="tbl-scroll">
    <table class="data scorecard">
      <colgroup><col style="width:190px"><col style="width:150px"><col></colgroup>
      <thead><tr><th>Role factor</th><th class="sc">Score</th><th>Why this score</th></tr></thead>
      <tbody>
{chr(10).join(rows)}
{total}
      </tbody>
    </table>
    </div>
    <div class="callout"><span class="lbl">How to read it</span><p>Weights are an editorial decomposition of the role's stated priority order &mdash; not an in-game formula. Bar length shows how fully each factor is earned; the longest factors carried the score, the shortest are where it gave points away. See <a href="../general/rating-methodology.html">how ships are rated</a>.</p></div>
  </section>
"""


SECNUM_RE = re.compile(r'<span class="sec-num">(\d+)</span>')
QNSIDE_RE = re.compile(r'<span class="qn-side">(\d+)</span>')
EXISTING_RE = re.compile(r'  <!-- Why This Rating -->\n  <section id="%s">.*?\n  </section>\n' % ANCHOR, re.S)


def target_secnum(html: str) -> int:
    m = re.search(r'<section id="%s">.*?<span class="sec-num">(\d+)</span>' % TARGET, html, re.S)
    if not m:
        raise ValueError(f"no #{TARGET} section found")
    return int(m.group(1))


def existing_secnum(html: str) -> int:
    m = re.search(r'<section id="%s">.*?<span class="sec-num">(\d+)</span>' % ANCHOR, html, re.S)
    return int(m.group(1))


def bump_numbers(html: str, n: int) -> str:
    html = SECNUM_RE.sub(lambda m: f'<span class="sec-num">{int(m.group(1)) + 1:02d}</span>'
                         if int(m.group(1)) >= n else m.group(0), html)
    html = QNSIDE_RE.sub(lambda m: f'<span class="qn-side">{int(m.group(1)) + 1:02d}</span>'
                         if int(m.group(1)) >= n else m.group(0), html)
    return html


def insert_qn(html: str, n: int) -> str:
    new = (f'<a class="qn-item" href="#{ANCHOR}"><span class="qn-dot amber"></span>'
           f'<span class="qn-nm">Why This Rating</span><span class="qn-side">{n:02d}</span></a>')
    return re.sub(r'\n([ \t]*)<a class="qn-item" href="#%s">' % TARGET,
                  lambda m: f'\n{m.group(1)}{new}\n{m.group(1)}<a class="qn-item" href="#{TARGET}">',
                  html, count=1)


def process(html: str, role: str, rating: int, weights: dict, sc: dict):
    """Return (new_html, action)."""
    if f'id="{ANCHOR}"' in html:                      # UPDATE in place
        num = existing_secnum(html)
        section = build_section(num, role, rating, weights, sc)
        new_html, n = EXISTING_RE.subn(section, html)
        if n != 1:
            raise ValueError("could not replace existing scorecard section")
        return new_html, ("unchanged" if new_html == html else "updated")
    # INSERT
    n = target_secnum(html)
    html = bump_numbers(html, n)
    html = insert_qn(html, n)
    section = build_section(n, role, rating, weights, sc)
    html, cnt = re.subn(r'(\n)([ \t]*)<section id="%s">' % TARGET,
                        lambda m: f'{m.group(1)}{section}{m.group(2)}<section id="{TARGET}">',
                        html, count=1)
    if cnt != 1:
        raise ValueError(f"could not insert before #{TARGET}")
    return html, "inserted"


def main(argv):
    flt = [a for a in argv if not a.startswith("-")]
    check = "--check" in argv
    counts = {"inserted": 0, "updated": 0, "unchanged": 0, "skipped": 0, "error": 0}
    changed = []
    for role in ROLES:
        doc = json.loads((DATA / f"{role}.json").read_text(encoding="utf-8"))
        weights = {w["factor"]: w["weight"] for w in doc.get("scorecard_weights", [])}
        for r in doc["ratings"]:
            sc = r.get("scorecard")
            if not sc or not r.get("dossier"):
                continue
            if flt and not any(f in r["dossier"] for f in flt):
                continue
            path = DOSSIERS / r["dossier"]
            if not path.exists():
                print(f"  ! missing dossier {r['dossier']}")
                counts["error"] += 1
                continue
            html = path.read_text(encoding="utf-8")
            try:
                new_html, action = process(html, role, r["rating"], weights, sc)
            except ValueError as e:
                print(f"  ! {r['dossier']}: {e}")
                counts["error"] += 1
                continue
            counts[action] = counts.get(action, 0) + 1
            tag = action.upper()
            if action in ("inserted", "updated") and not check:
                path.write_text(new_html, encoding="utf-8")
                changed.append(path)
            if action != "unchanged":
                print(f"  {tag:<9} {r['dossier']}  ({r['ship']} · {r['rating']})")
    mode = " [--check, nothing written]" if check else ""
    print(f"done{mode} — inserted {counts['inserted']}, updated {counts['updated']}, "
          f"unchanged {counts['unchanged']}, errors {counts['error']}")
    if counts["inserted"]:
        print("  NOTE: new sections added — re-run scripts/generate-anchor-files.sh")
    # Keep the regenerated scorecard's cross-links alive across rebuilds (idempotent; relink.py).
    if changed:
        print(f"\nrelinking {len(changed)} rebuilt dossier(s)…")
        from relink import relink
        relink(changed)
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
